import os
import time
import tempfile
from pathlib import Path

os.environ["SIFT_HOME"] = tempfile.mkdtemp()  # must be set before importing app

from fastapi.testclient import TestClient
import app as agent

client = TestClient(agent.app)
H = {"X-Sift-Token": agent.TOKEN}


def wait_scan():
    for _ in range(100):
        if not client.get("/scan/status", headers=H).json()["running"]:
            return
        time.sleep(0.1)
    raise AssertionError("scan never finished")


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True


def test_add_folder_invalid():
    res = client.post("/folders", json={"path": "C:/non_existent_folder_xyz_123"}, headers=H)
    assert res.status_code == 400


def test_indexing_search_and_deletion_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        note_file = tmp_path / "lecture_circuits.txt"
        note_file.write_text(
            "Thevenin's theorem states that any linear electrical network with voltage and current sources "
            "can be replaced by an equivalent voltage source in series with an equivalent resistance. "
            "Norton's theorem provides the dual current source equivalent.",
            encoding="utf-8",
        )

        # 1. Add folder
        res_folder = client.post("/folders", json={"path": str(tmp_path)}, headers=H)
        assert res_folder.status_code == 200
        assert str(tmp_path.resolve()) in res_folder.json()["added"]

        # 2. Run scan (asynchronous 202)
        res_scan = client.post("/scan", headers=H)
        assert res_scan.status_code == 202
        wait_scan()
        assert client.get("/scan/status", headers=H).json()["indexed"] >= 1

        # 3. Rescan without changes -> skipped/unchanged
        res_rescan = client.post("/scan", headers=H)
        assert res_rescan.status_code == 202
        wait_scan()
        assert client.get("/scan/status", headers=H).json()["unchanged"] >= 1

        # 4. Search for keyword
        res_search = client.get("/search", params={"q": "Thevenin"}, headers=H)
        assert res_search.status_code == 200
        results = res_search.json()
        assert len(results) >= 1
        assert "Thevenin" in results[0]["snippet"]
        assert any(str(note_file.resolve()) == r["file"] for r in results)

        # 5. Injection & syntax resilience test (special characters should not crash FTS5)
        res_weird = client.get("/search", params={"q": "AND OR NOT * \" ' ()"}, headers=H)
        assert res_weird.status_code == 200

        # 6. Delete index
        res_del = client.delete("/index", headers=H)
        assert res_del.status_code == 200
        assert res_del.json()["deleted"] is True

        # 7. Search after delete -> empty
        res_empty = client.get("/search", params={"q": "Thevenin"}, headers=H)
        assert res_empty.status_code == 200
        assert len(res_empty.json()) == 0
