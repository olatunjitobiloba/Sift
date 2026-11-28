import json
import pathlib
import sqlite3
import sys
import time

folder = sys.argv[1] if len(sys.argv) > 1 else "sample_lecture_notes"
qfile = sys.argv[2] if len(sys.argv) > 2 else "eval/queries.json"

with open(qfile, "r", encoding="utf-8") as f:
    queries = json.load(f)

conn = sqlite3.connect(":memory:")
conn.execute("CREATE VIRTUAL TABLE docs USING fts5(file UNINDEXED, body);")

chunks_count = 0
for p in pathlib.Path(folder).rglob("*"):
    if p.suffix.lower() in (".txt", ".md"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for part in text.split("\n\n"):
            cleaned = part.strip()
            if cleaned:
                conn.execute("INSERT INTO docs(file, body) VALUES (?, ?)", (p.name, cleaned[:1000]))
                chunks_count += 1

print(f"Indexed {chunks_count} chunks into in-memory SQLite FTS5")

hits, rr = 0, 0.0
detailed_results = []

def sanitize_query(q: str) -> str:
    tokens = [t for t in q.split() if t.isalnum()]
    if not tokens:
        return '""'
    # FTS5 OR search to give keyword search the best possible chance
    return " OR ".join(f'"{t}"' for t in tokens)

for item in queries:
    target = item.get("file") or item.get("expected")
    q_fts = sanitize_query(item["q"])
    
    cur = conn.execute(
        "SELECT file, bm25(docs) as score FROM docs WHERE docs MATCH ? ORDER BY score LIMIT 20",
        (q_fts,)
    )
    rows = cur.fetchall()
    
    ranked = []
    for file, _ in rows:
        if file not in ranked:
            ranked.append(file)
            
    if target in ranked:
        rank = ranked.index(target) + 1
        rr += 1 / rank
        is_hit = rank <= 5
        hits += int(is_hit)
        detailed_results.append({"q": item["q"], "target": target, "rank": rank, "top": ranked[:3]})
    else:
        detailed_results.append({"q": item["q"], "target": target, "rank": None, "top": ranked[:3]})

n = len(queries)
recall5 = hits / n if n > 0 else 0.0
mrr = rr / n if n > 0 else 0.0

print(f"\n--- Keyword (FTS5 BM25) Baseline Results ---")
print(f"recall@5 = {recall5:.2f}   MRR = {mrr:.2f}   ({n} queries)")

for r in detailed_results:
    status = f"Rank {r['rank']}" if r['rank'] is not None else "NOT FOUND"
    print(f"  [{status:<10}] Query: \"{r['q']}\" -> Expected: {r['target']}")
