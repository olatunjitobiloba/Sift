import numpy as np

_model = None


def _get_model():
    global _model
    if _model is None:  # loads on first use only
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def rank_chunks(rows, q: str, limit: int = 10):
    """rows: list of (path, text). Returns the best paths by meaning."""
    if not rows:
        return []
    m = _get_model()
    texts = [t or "" for _, t in rows]
    E = m.encode(texts, normalize_embeddings=True, batch_size=32)
    qv = m.encode([q], normalize_embeddings=True)[0]
    out, seen = [], set()
    for i in np.argsort(-(E @ qv)):
        path = rows[i][0]
        if path not in seen:
            seen.add(path)
            out.append((path, rows[i][1], float(E[i] @ qv)))
        if len(out) == limit:
            break
    return out


def rank_hybrid(rows, q: str, limit: int = 10, k: int = 60):
    """rows: list of (path, text). Returns the best paths by hybrid FTS + embeddings."""
    if not rows:
        return []
    import sqlite3

    con = sqlite3.connect(":memory:")
    con.execute("CREATE VIRTUAL TABLE c USING fts5(body)")
    con.executemany(
        "INSERT INTO c(rowid, body) VALUES (?, ?)",
        [(i, t or "") for i, (_, t) in enumerate(rows)],
    )

    terms = [t.replace('"', "") for t in q.split() if t.strip('"')]
    k_order = []
    if terms:
        match = " ".join(f'"{t}"' for t in terms)
        try:
            k_rows = con.execute(
                "SELECT rowid FROM c WHERE c MATCH ? ORDER BY bm25(c)",
                (match,),
            ).fetchall()
            k_order = [r[0] for r in k_rows]
        except Exception:
            k_order = []

    m = _get_model()
    texts = [t or "" for _, t in rows]
    E = m.encode(texts, normalize_embeddings=True, batch_size=32)
    qv = m.encode([q], normalize_embeddings=True)[0]
    e_order = list(np.argsort(-(E @ qv)))

    # Reciprocal Rank Fusion
    score = {}
    for lst in (k_order, e_order):
        for r, i in enumerate(lst):
            score[i] = score.get(i, 0) + 1 / (k + r + 1)
    fused_order = sorted(score, key=score.get, reverse=True)

    out, seen = [], set()
    for i in fused_order:
        path = rows[i][0]
        if path not in seen:
            seen.add(path)
            out.append((path, rows[i][1], float(score[i])))
        if len(out) == limit:
            break
    return out
