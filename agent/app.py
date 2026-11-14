import os
import re
import sqlite3
import hashlib
import secrets
from pathlib import Path
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from pypdf import PdfReader

HOME = Path(os.environ.get("SIFT_HOME", Path.home() / ".sift"))
HOME.mkdir(parents=True, exist_ok=True)
DB_PATH = HOME / "index.db"
TOKEN_PATH = HOME / "token"
TEXT_EXT = {".txt", ".md", ".pdf"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}

if not TOKEN_PATH.exists():
    TOKEN_PATH.write_text(secrets.token_urlsafe(32), encoding="utf-8")
TOKEN = TOKEN_PATH.read_text(encoding="utf-8").strip()

key_header = APIKeyHeader(name="X-Sift-Token", auto_error=False)


def require_token(k: str = Depends(key_header)):
    if not k or not secrets.compare_digest(k, TOKEN):
        raise HTTPException(status_code=401, detail="Missing or wrong token")


auth = [Depends(require_token)]

app = FastAPI(title="Sift agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@contextmanager
def get_db():
    """Manages SQLite connection lifecycle and guarantees closure on Windows."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE TABLE IF NOT EXISTS folders(path TEXT PRIMARY KEY)")
    conn.execute("CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, hash TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT)")
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(path UNINDEXED, text)")
    try:
        with conn:
            yield conn
    finally:
        conn.close()


db = get_db


def is_paused(c):
    row = c.execute("SELECT value FROM settings WHERE key='paused'").fetchone()
    return bool(row and row[0] == "1")


class Folder(BaseModel):
    path: str


def chunk(text: str, size: int = 800):
    parts, buf = [], ""
    for para in re.split(r"\n\s*\n", text):
        if len(buf) + len(para) > size and buf:
            parts.append(buf.strip())
            buf = ""
        buf += para + "\n\n"
    if buf.strip():
        parts.append(buf.strip())
    return parts


def extract(fp: Path) -> str:
    if fp.suffix.lower() == ".pdf":
        reader = PdfReader(str(fp))
        return "\n\n".join((p.extract_text() or "") for p in reader.pages)
    return fp.read_text(encoding="utf-8", errors="ignore")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/folders", dependencies=auth)
def list_folders():
    with db() as c:
        return [r[0] for r in c.execute("SELECT path FROM folders ORDER BY path")]


@app.post("/folders", dependencies=auth)
def add_folder(f: Folder):
    p = Path(f.path).expanduser().resolve()
    if not p.is_dir():
        raise HTTPException(status_code=400, detail="Not a folder")
    with db() as c:
        c.execute("INSERT OR IGNORE INTO folders VALUES (?)", (str(p),))
    return {"added": str(p)}


@app.delete("/folders", dependencies=auth)
def remove_folder(f: Folder):
    p = str(Path(f.path).expanduser().resolve())
    n = len(p)
    with db() as c:
        c.execute("DELETE FROM folders WHERE path=?", (p,))
        c.execute("DELETE FROM chunks WHERE substr(path,1,?)=?", (n, p))
        c.execute("DELETE FROM files WHERE substr(path,1,?)=?", (n, p))
    return {"removed": p}


@app.post("/scan", dependencies=auth)
def scan():
    seen = skipped = failed = 0
    with db() as c:
        if is_paused(c):
            raise HTTPException(status_code=409, detail="Indexing is paused")
        folders = [r[0] for r in c.execute("SELECT path FROM folders")]
        for folder in folders:
            fpath = Path(folder)
            if not fpath.exists():
                continue
            for fp in fpath.rglob("*"):
                if fp.suffix.lower() not in TEXT_EXT or not fp.is_file():
                    continue
                if any(part in SKIP_DIRS for part in fp.parts):
                    continue
                try:
                    text = extract(fp)
                except Exception:
                    failed += 1
                    continue
                h = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
                row = c.execute("SELECT hash FROM files WHERE path=?", (str(fp),)).fetchone()
                if row and row[0] == h:
                    skipped += 1
                    continue
                c.execute("DELETE FROM chunks WHERE path=?", (str(fp),))
                for part in chunk(text):
                    c.execute("INSERT INTO chunks VALUES (?, ?)", (str(fp), part))
                c.execute("INSERT OR REPLACE INTO files VALUES (?, ?)", (str(fp), h))
                seen += 1
    return {"indexed": seen, "unchanged": skipped, "failed": failed}


@app.get("/search", dependencies=auth)
def search(q: str, limit: int = 10):
    # quote each word so user text cannot break FTS5 syntax
    terms = [t.replace('"', "") for t in q.split() if t.strip('"')]
    if not terms:
        return []
    match = " ".join(f'"{t}"' for t in terms)
    with db() as c:
        rows = c.execute(
            "SELECT path, snippet(chunks, 1, '[', ']', '...', 12), bm25(chunks) "
            "FROM chunks WHERE chunks MATCH ? ORDER BY bm25(chunks) LIMIT ?",
            (match, min(limit, 50)),
        ).fetchall()
    return [{"file": r[0], "snippet": r[1], "score": -r[2]} for r in rows]


@app.get("/status", dependencies=auth)
def status():
    with db() as c:
        return {
            "folders": c.execute("SELECT COUNT(*) FROM folders").fetchone()[0],
            "files": c.execute("SELECT COUNT(*) FROM files").fetchone()[0],
            "chunks": c.execute("SELECT COUNT(*) FROM chunks").fetchone()[0],
            "paused": is_paused(c),
        }


@app.post("/pause", dependencies=auth)
def pause():
    with db() as c:
        c.execute("INSERT OR REPLACE INTO settings VALUES ('paused','1')")
    return {"paused": True}


@app.post("/resume", dependencies=auth)
def resume():
    with db() as c:
        c.execute("INSERT OR REPLACE INTO settings VALUES ('paused','0')")
    return {"paused": False}


@app.delete("/index", dependencies=auth)
def delete_index():
    with db() as c:
        c.execute("DELETE FROM chunks")
        c.execute("DELETE FROM files")
    return {"deleted": True}
