import re
import sqlite3
import hashlib
from pathlib import Path
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH = Path.home() / ".sift" / "index.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
TEXT_EXT = {".txt", ".md"}

app = FastAPI(title="Sift Agent", version="0.1.0")

# Enable CORS for Sharon's local React UI (Vite default: 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
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
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(path UNINDEXED, text)")
    try:
        with conn:
            yield conn
    finally:
        conn.close()


class Folder(BaseModel):
    path: str


def chunk(text: str, size: int = 800):
    """Splits text into paragraph-aware chunks for full-text indexing."""
    parts, buf = [], ""
    for para in re.split(r"\n\s*\n", text):
        if len(buf) + len(para) > size and buf:
            parts.append(buf.strip())
            buf = ""
        buf += para + "\n\n"
    if buf.strip():
        parts.append(buf.strip())
    return parts


@app.get("/health")
def health():
    return {"ok": True, "service": "sift-agent", "db": str(DB_PATH)}


@app.get("/folders")
def list_folders():
    with get_db() as conn:
        rows = conn.execute("SELECT path FROM folders").fetchall()
    return {"folders": [r[0] for r in rows]}


@app.post("/folders")
def add_folder(f: Folder):
    p = Path(f.path).expanduser().resolve()
    if not p.is_dir():
        raise HTTPException(status_code=400, detail=f"'{f.path}' is not a valid directory")
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO folders VALUES (?)", (str(p),))
    return {"added": str(p)}


@app.post("/scan")
def scan():
    seen = 0
    skipped = 0
    with get_db() as conn:
        folders = [r[0] for r in conn.execute("SELECT path FROM folders").fetchall()]
        for folder in folders:
            folder_path = Path(folder)
            if not folder_path.exists():
                continue
            for fp in folder_path.rglob("*"):
                if fp.suffix.lower() not in TEXT_EXT or not fp.is_file():
                    continue
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue

                h = hashlib.sha256(text.encode()).hexdigest()
                row = conn.execute("SELECT hash FROM files WHERE path=?", (str(fp),)).fetchone()
                if row and row[0] == h:
                    skipped += 1
                    continue

                # Remove previous chunks if file was modified
                conn.execute("DELETE FROM chunks WHERE path=?", (str(fp),))
                for part in chunk(text):
                    conn.execute("INSERT INTO chunks VALUES (?, ?)", (str(fp), part))
                conn.execute("INSERT OR REPLACE INTO files VALUES (?, ?)", (str(fp), h))
                seen += 1

    return {"indexed": seen, "unchanged": skipped}


@app.get("/search")
def search(q: str, limit: int = 10):
    # Sanitize each term so punctuation/operators cannot break FTS5 MATCH syntax
    terms = [t.replace('"', "") for t in q.split() if t.strip('"')]
    if not terms:
        return []
    match = " ".join(f'"{t}"' for t in terms)
    with get_db() as conn:
        rows = conn.execute(
            "SELECT path, snippet(chunks, 1, '[', ']', '...', 12), bm25(chunks) "
            "FROM chunks WHERE chunks MATCH ? ORDER BY bm25(chunks) LIMIT ?",
            (match, min(limit, 50)),
        ).fetchall()
    return [{"file": r[0], "snippet": r[1], "score": round(-r[2], 4)} for r in rows]


@app.delete("/index")
def delete_index():
    with get_db() as conn:
        conn.execute("DELETE FROM chunks")
        conn.execute("DELETE FROM files")
    return {"deleted": True}
