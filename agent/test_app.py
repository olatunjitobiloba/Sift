import os
import time
import tempfile
from pathlib import Path

os.environ["SIFT_HOME"] = tempfile.mkdtemp()  # must be set before importing app

from fastapi.testclient import TestClient
import app as agent

client = TestClient(agent.app)
H = {"X-Sift-Token": agent.TOKEN}


def make_folder(text="Deadlock happens when two threads wait on each other."):
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "os.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    return d


def wait_scan():
    for _ in range(100):
        if not client.get("/scan/status", headers=H).json()["running"]:
            return
        time.sleep(0.1)
    raise AssertionError("scan never finished")


def test_health_is_open():
    assert client.get("/health").status_code == 200


def test_token_required():
    assert client.get("/status").status_code == 401
    assert client.get("/status", headers={"X-Sift-Token": "wrong"}).status_code == 401


def test_index_and_search():
    d = make_folder()
    client.post("/folders", json={"path": d}, headers=H)
    assert client.post("/scan", headers=H).status_code == 202
    wait_scan()
    assert client.get("/scan/status", headers=H).json()["indexed"] >= 1
    hits = client.get("/search", params={"q": "deadlock"}, headers=H).json()
    assert len(hits) >= 1


def test_odd_query_does_not_crash():
    r = client.get("/search", params={"q": '" OR * ('}, headers=H)
    assert r.status_code == 200


def test_pause_blocks_scan():
    client.post("/pause", headers=H)
    assert client.post("/scan", headers=H).status_code == 409
    client.post("/resume", headers=H)


def test_delete_index_empties_search():
    client.delete("/index", headers=H)
    assert client.get("/search", params={"q": "deadlock"}, headers=H).json() == []


def test_folder_management():
    d = tempfile.mkdtemp()
    res_add = client.post("/folders", json={"path": d}, headers=H)
    assert res_add.status_code == 200

    res_list = client.get("/folders", headers=H)
    assert res_list.status_code == 200
    assert any(os.path.samefile(p, d) if os.path.exists(p) else p == d for p in res_list.json())

    res_del = client.request("DELETE", "/folders", json={"path": d}, headers=H)
    assert res_del.status_code == 200
    assert str(res_del.json()["removed"]) == str(Path(d).expanduser().resolve())
