import json
import pathlib
import sys
import time
import numpy as np
from sentence_transformers import SentenceTransformer

if len(sys.argv) < 3:
    print("Usage: python eval/spike_embed.py <path/to/eval_folder> <eval/queries.json>")
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

model = SentenceTransformer("all-MiniLM-L6-v2")
t = time.time()
E = model.encode(chunks, normalize_embeddings=True, batch_size=32)
embed_time = time.time() - t
print(f"{len(chunks)} chunks embedded in {embed_time:.2f}s ({len(chunks)/embed_time:.1f} chunks/sec)")

Q = model.encode([x["q"] for x in queries], normalize_embeddings=True)
hits, rr = 0, 0.0
detailed_results = []

for item, qv in zip(queries, Q):
    target = item.get("file") or item.get("expected")
    sims = E @ qv
    sorted_indices = np.argsort(-sims)
    
    ranked = []
    for i in sorted_indices:
        if owners[i] not in ranked:  # one rank per file
            ranked.append(owners[i])
            
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

print(f"\n--- Embedding Spike Results ---")
print(f"recall@5 = {recall5:.2f}   MRR = {mrr:.2f}   ({n} queries)")

for r in detailed_results:
    status = f"Rank {r['rank']}" if r['rank'] is not None else "NOT FOUND"
    print(f"  [{status:<10}] Query: \"{r['q']}\" -> Expected: {r['target']}")
