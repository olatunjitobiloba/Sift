import os
import sys
import tempfile
import time
from pathlib import Path
import httpx

URL = os.environ.get("SIFT_URL", "http://127.0.0.1:8765")
TOKEN = os.environ.get("SIFT_TOKEN")

if not TOKEN:
    token_file = Path.home() / ".sift" / "token"
    if token_file.exists():
        TOKEN = token_file.read_text(encoding="utf-8").strip()

if not TOKEN:
    print("Error: SIFT_TOKEN not set and ~/.sift/token not found.")
    sys.exit(1)

H = {"X-Sift-Token": TOKEN}

# Probe URL with fallback to 8766 if 8765 is not listening
try:
    res = httpx.get(f"{URL}/health", timeout=2.0)
except Exception:
    if "8765" in URL:
        URL = "http://127.0.0.1:8766"
        res = httpx.get(f"{URL}/health", timeout=2.0)
    else:
        raise

assert res.status_code == 200
d = tempfile.mkdtemp()
with open(os.path.join(d, "n.txt"), "w", encoding="utf-8") as f:
    f.write("smoketest keyword")

httpx.post(f"{URL}/folders", json={"path": d}, headers=H)
assert httpx.post(f"{URL}/scan", headers=H).status_code in (202, 409)
for _ in range(100):
    if not httpx.get(f"{URL}/scan/status", headers=H).json()["running"]:
        break
    time.sleep(0.1)

hits = httpx.get(f"{URL}/search", params={"q": "smoketest"}, headers=H).json()
assert hits, "search returned nothing"
print("smoke OK")
