import os
import re
import fnmatch
import sqlite3
import hashlib
import secrets
import threading
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

SCAN = {
    "running": False,
    "done": 0,
    "total": 0,
    "indexed": 0,
    "unchanged": 0,
    "failed": 0,
    "removed": 0,
}

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
    conn.execute("CREATE TABLE IF NOT EXISTS excludes(pattern TEXT PRIMARY KEY)")
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


class Pattern(BaseModel):
    pattern: str


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


def excluded(fp: Path, patterns):
    return any(fnmatch.fnmatch(part, pat) for part in fp.parts for pat in patterns)


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
    prefix = p + os.sep
    n = len(prefix)
    with db() as c:
        c.execute("DELETE FROM folders WHERE path=?", (p,))
        c.execute("DELETE FROM chunks WHERE substr(path,1,?)=?", (n, prefix))
        c.execute("DELETE FROM files WHERE substr(path,1,?)=?", (n, prefix))
    return {"removed": p}


@app.get("/excludes", dependencies=auth)
def list_excludes():
    with db() as c:
        return [r[0] for r in c.execute("SELECT pattern FROM excludes ORDER BY pattern")]


@app.post("/excludes", dependencies=auth)
def add_exclude(p: Pattern):
    pat = p.pattern.strip()
    if not pat:
        raise HTTPException(400, "Empty pattern")
    with db() as c:
        c.execute("INSERT OR IGNORE INTO excludes VALUES (?)", (pat,))
    return {"added": pat}


@app.delete("/excludes", dependencies=auth)
def remove_exclude(p: Pattern):
    with db() as c:
        c.execute("DELETE FROM excludes WHERE pattern=?", (p.pattern,))
    return {"removed": p.pattern}


@app.get("/files", dependencies=auth)
def list_files(limit: int = 100, offset: int = 0):
    with db() as c:
        rows = c.execute(
            "SELECT path FROM files ORDER BY path LIMIT ? OFFSET ?",
            (min(limit, 500), offset),
        ).fetchall()
    return [r[0] for r in rows]


def do_scan():
    try:
        with db() as c:
            folders = [r[0] for r in c.execute("SELECT path FROM folders")]
            pats = [r[0] for r in c.execute("SELECT pattern FROM excludes")]
            files = []
            for folder in folders:
                folder_path = Path(folder)
                if not folder_path.exists():
                    continue
                for fp in folder_path.rglob("*"):
                    if (
                        fp.suffix.lower() in TEXT_EXT
                        and fp.is_file()
                        and not any(p in SKIP_DIRS for p in fp.parts)
                        and not excluded(fp, pats)
                    ):
                        files.append(fp)
            SCAN.update(total=len(files), done=0, indexed=0, unchanged=0, failed=0, removed=0)
            for fp in files:
                if is_paused(c):
                    break
                SCAN["done"] += 1
                try:
                    text = extract(fp)
                except Exception:
                    SCAN["failed"] += 1
                    continue
                h = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
                row = c.execute("SELECT hash FROM files WHERE path=?", (str(fp),)).fetchone()
                if row and row[0] == h:
                    SCAN["unchanged"] += 1
                    continue
                c.execute("DELETE FROM chunks WHERE path=?", (str(fp),))
                for part in chunk(text):
                    c.execute("INSERT INTO chunks VALUES (?, ?)", (str(fp), part))
                c.execute("INSERT OR REPLACE INTO files VALUES (?, ?)", (str(fp), h))
                SCAN["indexed"] += 1
                c.commit()

            keep = {str(f) for f in files}
            for (p,) in c.execute("SELECT path FROM files").fetchall():
                if p not in keep:
                    c.execute("DELETE FROM chunks WHERE path=?", (p,))
                    c.execute("DELETE FROM files WHERE path=?", (p,))
                    SCAN["removed"] += 1

            roots = [r[0] + os.sep for r in c.execute("SELECT path FROM folders")]
            for (p,) in c.execute("SELECT path FROM files").fetchall():
                if not any(p.startswith(r) for r in roots):
                    c.execute("DELETE FROM chunks WHERE path=?", (p,))
                    c.execute("DELETE FROM files WHERE path=?", (p,))
                    SCAN["removed"] += 1
            c.commit()
    finally:
        SCAN["running"] = False


@app.post("/scan", dependencies=auth, status_code=202)
def scan():
    with db() as c:
        if is_paused(c):
            raise HTTPException(409, "Indexing is paused")
    if SCAN["running"]:
        raise HTTPException(409, "Scan already running")
    SCAN["running"] = True
    threading.Thread(target=do_scan, daemon=True).start()
    return {"started": True}


@app.get("/scan/status", dependencies=auth)
def scan_status():
    return SCAN


@app.get("/search", dependencies=auth)
def search(q: str, limit: int = 10, ext: str = "", folder: str = ""):
    # quote each word so user text cannot break FTS5 syntax
    terms = [t.replace('"', "") for t in q.split() if t.strip('"')]
    if not terms:
        return []
    match = " ".join(f'"{t}"' for t in terms)
    limit = min(limit, 50)
    sql = ("SELECT path, snippet(chunks, 1, '[', ']', '...', 12), bm25(chunks) "
           "FROM chunks WHERE chunks MATCH ?")
    args = [match]
    if ext:
        e = "." + re.sub(r"[^a-z0-9]", "", ext.lower())
        sql += " AND lower(path) LIKE ?"
        args.append("%" + e)
    if folder:
        pre = str(Path(folder).expanduser().resolve()) + os.sep
        sql += " AND substr(path,1,?)=?"
        args += [len(pre), pre]
    sql += " ORDER BY bm25(chunks) LIMIT ?"
    args.append(limit * 5)  # fetch extra, then keep one chunk per file
    with db() as c:
        rows = c.execute(sql, args).fetchall()
    out, seen = [], set()
    for path, snip, score in rows:
        if path in seen:
            continue
        seen.add(path)
        out.append({"file": path, "snippet": snip, "score": -score})
        if len(out) == limit:
            break
    return out


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
