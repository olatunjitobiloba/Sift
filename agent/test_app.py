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


def test_pause_mid_scan_halts():
    d = tempfile.mkdtemp()
    for i in range(20):
        with open(os.path.join(d, f"note_{i}.txt"), "w", encoding="utf-8") as f:
            f.write(f"Sample note content {i} for pause test\n" * 50)
    client.post("/folders", json={"path": d}, headers=H)
    client.post("/scan", headers=H)
    client.post("/pause", headers=H)
    wait_scan()
    status = client.get("/scan/status", headers=H).json()
    assert not status["running"]
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


def test_deleted_file_leaves_index():
    d = make_folder("zebra crossing rules")
    client.post("/folders", json={"path": d}, headers=H)
    client.post("/scan", headers=H)
    wait_scan()
    assert len(client.get("/search", params={"q": "zebra"}, headers=H).json()) >= 1
    os.remove(os.path.join(d, "os.txt"))
    client.post("/scan", headers=H)
    wait_scan()
    assert client.get("/search", params={"q": "zebra"}, headers=H).json() == []


def test_exclude_pattern():
    d = make_folder("quokka habitat")
    client.post("/folders", json={"path": d}, headers=H)
    client.post("/excludes", json={"pattern": "os.txt"}, headers=H)
    client.post("/scan", headers=H)
    wait_scan()
    assert client.get("/search", params={"q": "quokka"}, headers=H).json() == []
    client.request("DELETE", "/excludes", json={"pattern": "os.txt"}, headers=H)


def test_list_files_and_excludes():
    d = make_folder("sample file test")
    client.post("/folders", json={"path": d}, headers=H)
    client.post("/scan", headers=H)
    wait_scan()
    files = client.get("/files", headers=H).json()
    assert len(files) >= 1
    assert any("os.txt" in f for f in files)

    client.post("/excludes", json={"pattern": "*.secret"}, headers=H)
    excludes = client.get("/excludes", headers=H).json()
    assert "*.secret" in excludes
    client.request("DELETE", "/excludes", json={"pattern": "*.secret"}, headers=H)
    assert "*.secret" not in client.get("/excludes", headers=H).json()


def test_remove_folder_keeps_sibling():
    base = tempfile.mkdtemp()
    a, b = os.path.join(base, "notes"), os.path.join(base, "notes2")
    os.mkdir(a); os.mkdir(b)
    open(os.path.join(a, "a.txt"), "w").write("giraffe neck")
    open(os.path.join(b, "b.txt"), "w").write("giraffe tall")
    client.post("/folders", json={"path": a}, headers=H)
    client.post("/folders", json={"path": b}, headers=H)
    client.post("/scan", headers=H); wait_scan()
    client.request("DELETE", "/folders", json={"path": a}, headers=H)
    hits = client.get("/search", params={"q": "giraffe"}, headers=H).json()
    assert len(hits) == 1 and hits[0]["file"].endswith("b.txt")


def test_one_hit_per_file():
    d = tempfile.mkdtemp()
    text = "\n\n".join(["wombat " * 100] * 3)  # long enough for several chunks
    open(os.path.join(d, "w.txt"), "w").write(text)
    client.post("/folders", json={"path": d}, headers=H)
    client.post("/scan", headers=H); wait_scan()
    hits = client.get("/search", params={"q": "wombat"}, headers=H).json()
    assert len(hits) == 1


def test_ext_filter():
    d = tempfile.mkdtemp()
    open(os.path.join(d, "x.txt"), "w").write("platypus fact")
    open(os.path.join(d, "y.md"), "w").write("platypus fact")
    client.post("/folders", json={"path": d}, headers=H)
    client.post("/scan", headers=H); wait_scan()
    hits = client.get("/search", params={"q": "platypus", "ext": "md"}, headers=H).json()
    assert len(hits) == 1 and hits[0]["file"].endswith(".md")

