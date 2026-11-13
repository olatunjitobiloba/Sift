import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app import app, DB_PATH, get_db

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["service"] == "sift-agent"


def test_add_folder_invalid():
    res = client.post("/folders", json={"path": "C:/non_existent_folder_xyz_123"})
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
        res_folder = client.post("/folders", json={"path": str(tmp_path)})
        assert res_folder.status_code == 200
        assert str(tmp_path.resolve()) in res_folder.json()["added"]

        # 2. Run scan
        res_scan = client.post("/scan")
        assert res_scan.status_code == 200
        assert res_scan.json()["indexed"] >= 1

        # 3. Rescan without changes -> skipped/unchanged
        res_rescan = client.post("/scan")
        assert res_rescan.status_code == 200
        assert res_rescan.json()["unchanged"] >= 1

        # 4. Search for keyword
        res_search = client.get("/search", params={"q": "Thevenin"})
        assert res_search.status_code == 200
        results = res_search.json()
        assert len(results) >= 1
        assert "Thevenin" in results[0]["snippet"]
        assert str(note_file.resolve()) == results[0]["file"]

        # 5. Injection & syntax resilience test (special characters should not crash FTS5)
        res_weird = client.get("/search", params={"q": "AND OR NOT * \" ' ()"})
        assert res_weird.status_code == 200

        # 6. Delete index
        res_del = client.delete("/index")
        assert res_del.status_code == 200
        assert res_del.json()["deleted"] is True

        # 7. Search after delete -> empty
        res_empty = client.get("/search", params={"q": "Thevenin"})
        assert res_empty.status_code == 200
        assert len(res_empty.json()) == 0
