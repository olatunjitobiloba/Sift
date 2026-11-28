import json
import os
import sys
import time
from pathlib import Path
import httpx

URL = os.environ.get("SIFT_URL", "http://127.0.0.1:8765")
TOKEN = os.environ.get("SIFT_TOKEN")

if not TOKEN:
    sift_home = Path(os.environ.get("SIFT_HOME", Path.home() / ".sift"))
    token_file = sift_home / "token"
    if token_file.exists():
        TOKEN = token_file.read_text(encoding="utf-8").strip()

if not TOKEN:
    print("Error: SIFT_TOKEN environment variable is not set and ~/.sift/token not found.")
    sys.exit(1)


def _is_sift_agent(url: str) -> bool:
    try:
        r = httpx.get(f"{url}/health", timeout=2.0)
        return r.status_code == 200 and r.json().get("service") == "sift-agent"
    except Exception:
        return False


if not _is_sift_agent(URL):
    if "8765" in URL and _is_sift_agent("http://127.0.0.1:8766"):
        URL = "http://127.0.0.1:8766"

query_file = sys.argv[1] if len(sys.argv) > 1 else "queries.json"
with open(query_file, "r", encoding="utf-8") as f:
    queries = json.load(f)

hits5, rr = 0, 0.0
t0 = time.perf_counter()
for item in queries:
    target = item.get("expected") or item.get("file")
    try:
        res = httpx.get(
            f"{URL}/search",
            params={"q": item["q"], "limit": 5},
            headers={"X-Sift-Token": TOKEN},
            timeout=10.0,
        )
        res.raise_for_status()
        r = res.json()
    except Exception as e:
        print(f"Error connecting to agent at {URL}: {e}")
        sys.exit(1)

    names = [os.path.basename(x["file"]) for x in r]
    if target in names:
        hits5 += 1
        rr += 1 / (names.index(target) + 1)
    else:
        print("MISS:", item["q"])

elapsed_ms = (time.perf_counter() - t0) * 1000
n = len(queries)
if n > 0:
    print(f"recall@5 = {hits5/n:.2f}   MRR = {rr/n:.2f}   ({n} queries in {elapsed_ms:.1f} ms)")
else:
    print("No queries provided.")
