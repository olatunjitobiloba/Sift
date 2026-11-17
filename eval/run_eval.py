import json
import os
import sys
from pathlib import Path
import httpx

URL = os.environ.get("SIFT_URL", "http://127.0.0.1:8765")
TOKEN = os.environ.get("SIFT_TOKEN")

if not TOKEN:
    token_file = Path.home() / ".sift" / "token"
    if token_file.exists():
        TOKEN = token_file.read_text(encoding="utf-8").strip()

if not TOKEN:
    print("Error: SIFT_TOKEN environment variable is not set and ~/.sift/token not found.")
    sys.exit(1)

query_file = sys.argv[1] if len(sys.argv) > 1 else "queries.json"
with open(query_file, "r", encoding="utf-8") as f:
    queries = json.load(f)

hits5, rr = 0, 0.0
for item in queries:
    try:
        res = httpx.get(
            f"{URL}/search",
            params={"q": item["q"], "limit": 5},
            headers={"X-Sift-Token": TOKEN},
            timeout=10.0,
        )
        r = res.json()
    except Exception as e:
        print(f"Error connecting to agent at {URL}: {e}")
        sys.exit(1)

    names = [os.path.basename(x["file"]) for x in r]
    if item["expected"] in names:
        hits5 += 1
        rr += 1 / (names.index(item["expected"]) + 1)
    else:
        print("MISS:", item["q"])

n = len(queries)
if n > 0:
    print(f"recall@5 = {hits5/n:.2f}   MRR = {rr/n:.2f}   ({n} queries)")
else:
    print("No queries provided.")
