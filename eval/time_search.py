import json
import os
import shutil
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path


def _is_sift_agent(url: str) -> bool:
    try:
        with urllib.request.urlopen(url + "/health", timeout=2.0) as r:
            data = json.load(r)
            return r.status == 200 and data.get("service") == "sift-agent"
    except Exception:
        return False


BASE = os.environ.get("SIFT_URL", "http://127.0.0.1:8765")
if not _is_sift_agent(BASE) and "8765" in BASE and _is_sift_agent("http://127.0.0.1:8766"):
    BASE = "http://127.0.0.1:8766"

TOKEN = os.environ.get("SIFT_TOKEN")
if not TOKEN:
    sift_home = Path(os.environ.get("SIFT_HOME", Path.home() / ".sift"))
    token_file = sift_home / "token"
    if token_file.exists():
        TOKEN = token_file.read_text(encoding="utf-8").strip()

if not TOKEN:
    print("Error: SIFT_TOKEN environment variable is not set and ~/.sift/token not found.")
    sys.exit(1)

H = {"X-Sift-Token": TOKEN, "Content-Type": "application/json"}


def call(method: str, path: str, body=None):
    req = urllib.request.Request(
        BASE + path,
        method=method,
        headers=H,
        data=json.dumps(body).encode("utf-8") if body else None,
    )
    with urllib.request.urlopen(req, timeout=30.0) as resp:
        return json.load(resp)


max_wait_s = float(sys.argv[1]) if len(sys.argv) > 1 else 120.0
file_count = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

d = tempfile.mkdtemp(prefix="sift_1k_bench_")
try:
    for i in range(file_count):
        with open(os.path.join(d, f"f{i}.txt"), "w", encoding="utf-8") as f:
            f.write(f"note {i} about processes, threads, deadlock and scheduling. " * 20)

    call("POST", "/folders", {"path": d})
    t_scan_start = time.perf_counter()
    call("POST", "/scan")

    deadline = t_scan_start + max_wait_s
    while time.perf_counter() < deadline:
        scan_state = call("GET", "/scan/status")
        if not scan_state["running"]:
            break
        time.sleep(0.5)
    else:
        raise TimeoutError(f"Scan did not finish within {max_wait_s}s: {scan_state}")

    scan_elapsed = time.perf_counter() - t_scan_start
    agent_status = call("GET", "/status")
    assert scan_state["indexed"] >= file_count or agent_status["files"] >= file_count, (
        f"Incomplete index before timing: scan={scan_state}, status={agent_status}"
    )

    times = []
    queries = ["deadlock", "scheduling", "threads", "processes", "note"] * 4
    for q in queries:
        t = time.perf_counter()
        hits = call("GET", "/search?" + urllib.parse.urlencode({"q": q}))
        times.append(time.perf_counter() - t)
        assert len(hits) >= 1, f"Expected hits for {q!r}, got {hits}"

    times.sort()
    median_s = times[len(times) // 2]
    max_s = times[-1]
    min_s = times[0]

    print(
        f"url={BASE} indexed_files={agent_status['files']} chunks={agent_status['chunks']} "
        f"scan_s={scan_elapsed:.2f}s"
    )
    print(
        f"n={len(times)} min={min_s:.4f}s median={median_s:.4f}s max={max_s:.4f}s"
    )
finally:
    try:
        call("DELETE", "/folders", {"path": d})
    except Exception:
        pass
    shutil.rmtree(d, ignore_errors=True)
