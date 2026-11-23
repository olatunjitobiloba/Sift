import json
import pathlib
import sqlite3
import sys
import time
import numpy as np
from sentence_transformers import SentenceTransformer

if len(sys.argv) < 3:
    print("Usage: python eval/spike_hybrid.py <eval_folder> <queries.json>")
    sys.exit(1)

folder, qfile = sys.argv[1], sys.argv[2]
with open(qfile, "r", encoding="utf-8") as f:
    queries = json.load(f)

chunks, owners = [], []
for p in pathlib.Path(folder).rglob("*"):
    if p.suffix.lower() in (".txt", ".md"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for part in text.split("\n\n"):
            cleaned = part.strip()
            if cleaned:
                chunks.append(cleaned[:1000])
                owners.append(p.name)

print(f"Loaded {len(chunks)} text chunks across {len(set(owners))} files from {folder}")

# keyword side: same FTS5 + bm25 idea as the agent (implicit AND across tokens)
con = sqlite3.connect(":memory:")
con.execute("CREATE VIRTUAL TABLE c USING fts5(body)")
con.executemany(
    "INSERT INTO c(rowid, body) VALUES (?, ?)",
    [(i, t) for i, t in enumerate(chunks)]
)

def keyword_order(q):
    terms = [t.replace('"', "") for t in q.split() if t.strip('"')]
    if not terms:
        return []
    match = " ".join(f'"{t}"' for t in terms)
    try:
        rows = con.execute(
            "SELECT rowid FROM c WHERE c MATCH ? ORDER BY bm25(c)",
            (match,)
        ).fetchall()
        return [r[0] for r in rows]
    except Exception:
        return []

print("Loading SentenceTransformer('all-MiniLM-L6-v2')...")
model = SentenceTransformer("all-MiniLM-L6-v2")
t0 = time.time()
E = model.encode(chunks, normalize_embeddings=True, batch_size=32)
print(f"Encoded {len(chunks)} chunks in {time.time() - t0:.2f}s")

def files_from(order):
    out = []
    for i in order:
        if owners[i] not in out:
            out.append(owners[i])
    return out

def fuse(a, b, k=60):  # Reciprocal Rank Fusion
    score = {}
    for lst in (a, b):
        for r, i in enumerate(lst):
            score[i] = score.get(i, 0) + 1 / (k + r + 1)
    return sorted(score, key=score.get, reverse=True)

def report(name, ranked_per_query):
    hits, rr = 0, 0.0
    detailed = []
    for item, ranked in zip(queries, ranked_per_query):
        target = item.get("file") or item.get("expected")
        if target in ranked:
            rank = ranked.index(target) + 1
            rr += 1 / rank
            hits += int(rank <= 5)
            detailed.append((item["q"], target, rank))
        else:
            detailed.append((item["q"], target, None))
    n = len(queries)
    recall5 = hits / n if n > 0 else 0.0
    mrr = rr / n if n > 0 else 0.0
    print(f"{name:<12} recall@5 = {recall5:.2f}   MRR = {mrr:.2f}   (hits: {hits}/{n})")
    return recall5, mrr, detailed

kw, em, hy = [], [], []
for item in queries:
    k_order = keyword_order(item["q"])
    qv = model.encode([item["q"]], normalize_embeddings=True)[0]
    e_order = list(np.argsort(-(E @ qv)))
    kw.append(files_from(k_order))
    em.append(files_from(e_order))
    hy.append(files_from(fuse(k_order, e_order)))

print("\n--- Day 9 3-Way Search Benchmark ---")
kw_r5, kw_mrr, kw_det = report("keyword", kw)
em_r5, em_mrr, em_det = report("embedding", em)
hy_r5, hy_mrr, hy_det = report("hybrid", hy)

print("\nDetailed Per-Query Comparison:")
print(f"{'Query (Truncated)':<40} | {'Expected File':<28} | {'KW Rank':<8} | {'EM Rank':<8} | {'HY Rank':<8}")
print("-" * 105)
for (q, target, kr), (_, _, er), (_, _, hr) in zip(kw_det, em_det, hy_det):
    kr_str = f"Rank {kr}" if kr else "MISS"
    er_str = f"Rank {er}" if er else "MISS"
    hr_str = f"Rank {hr}" if hr else "MISS"
    print(f"{q[:38]:<40} | {target[:26]:<28} | {kr_str:<8} | {er_str:<8} | {hr_str:<8}")
