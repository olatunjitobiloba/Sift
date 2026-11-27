# Sift Week 13 Demo Script (5 Minutes)

> **Presentation Rule:** Say *"indexing and search run locally on your laptop."* Never claim *"100% private"* or *"100% secure."*

---

## 0. Scope Freeze (What Is In, Experimental, and Out)

- **In Demo (Core Verified):** Folder selection (`POST /folders`), exclusions (`POST /excludes`), keyword search (`GET /search`), pause/resume (`POST /pause`, `POST /resume`), index inspection & erasure (`GET /files`, `DELETE /index`), and mobile phone pairing.
- **Experimental (Labelled Clearly):** Meaning mode (`mode=meaning` / `mode=hybrid`) and audio transcript search — only shown if verified offline on the presenting laptop with cached model weights.
- **Out of Scope (Backlog):** Automated or human-in-the-loop file move suggestions (Issue [#11](https://github.com/olatunjitobiloba/Sift/issues/11), labelled `backlog`). Not included in this demo.

---

## 1. Pre-Flight Checklist (5 Minutes Before Presenting)

1. Confirm port `8765` is free (or run on `8766` if another local bridge occupies `8765`).
2. Confirm the synthetic demo folder [`demo/`](../demo) exists with 8 `.txt`/`.md` files (no personal/private files).
3. Record a 30-second backup screen capture of the working desktop + Expo mobile flow in advance.
4. Keep a mobile hotspot ready in case the demo room Wi-Fi isolates devices on the LAN.

---

## 2. Five-Minute Live Walkthrough

### Step 1: Start Agent & Prove Loopback Binding (0:00 – 0:40)
Start the local agent from `agent/`:
```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8765
```
Show the terminal output and run a quick socket check in a second terminal to confirm it listens on `127.0.0.1` only (not `0.0.0.0`):
```powershell
netstat -ano | findstr 8765
curl http://127.0.0.1:8765/health   # expects {"ok":true,"service":"sift-agent"}
```
Grab your token (`$TOKEN = Get-Content $HOME\.sift\token`) and show `GET /search` without the header returns `401 Unauthorized`.

### Step 2: Add `demo/`, Scan, and Search `"deadlock"` (0:40 – 1:30)
1. In the Web UI (or API), add the [`demo/`](../demo) folder.
2. Trigger Scan (`POST /scan`) and show progress telemetry (`GET /scan/status` -> 8 files indexed).
3. Search **`"deadlock"`**.
4. Point out the contextual `[deadlock]` snippet from `os_deadlocks.txt`, deduplicated to one card per matching file.

### Step 3: Add Exclusion, Rescan, and Verify Removal (1:30 – 2:15)
1. Show `private_budget.txt` currently appears in `"Indexed files"` (`GET /files`).
2. Add exclusion pattern `private_*` (`POST /excludes` with `{"pattern": "private_*"}`).
3. Re-run Scan (`POST /scan`) -> `removed: 1`.
4. Check `GET /files` and search `"private_demo_marker"`: `private_budget.txt` is gone from SQLite while untouched on disk.

### Step 4: Pause, Refuse Scan, and Resume (2:15 – 2:55)
1. Toggle **Pause** (`POST /pause` -> `{"paused": true}`).
2. Attempt to start a Scan (`POST /scan`): confirm it is refused with **HTTP 409** (`"Indexing is paused"`).
3. Toggle **Resume** (`POST /resume` -> `{"paused": false}`), run Scan (`POST /scan` -> `202 Accepted`), confirming normal operation resumes.

### Step 5: Open "Indexed Files", Delete Index, Verify Zero Results (2:55 – 3:35)
1. Open the **Indexed files** view (`GET /files`) showing all 7 remaining demo notes.
2. Click **Delete index** (`DELETE /index`).
3. Re-run the `"deadlock"` search and inspect `GET /files`: confirm **zero results** immediately, while files on disk inside `demo/` remain untouched.

### Step 6: Mobile Pairing & Search (3:35 – 4:15)
*(Trigger Step 2 scan again if needed before searching from mobile, or present Philip's backup screen recording if demo Wi-Fi blocks peer connections.)*
1. Show one-time pairing code generation and device pairing on the Expo mobile app.
2. Execute a query from the phone and show matching filename and snippet.

### Step 7: CI Gatekeeper & Evaluation Limits (4:15 – 5:00)
1. Open GitHub PR [#7](https://github.com/olatunjitobiloba/Sift/pull/7) and [`docs/CI.md`](./CI.md) showing the green `test` check (unit tests + `smoke.py`), plus the proof run where a broken test blocked merge (RED) before fixing (GREEN).
2. Present [`eval/BASELINE.md`](../eval/BASELINE.md) and [`eval/SPIKE.md`](../eval/SPIKE.md), explicitly noting the honest limits below.

---

## 3. Wi-Fi-Off Failure Rehearsal Log

Run the script twice with **Wi-Fi turned off** (or localhost-only isolation) prior to Week 13 presentation:
- **Pass 1 (Local Core Rehearsal — Fresh Clone Verification):** Cloned `feature/agent-skeleton` into an isolated temporary folder (`sift-fresh`), installed `agent/requirements.txt` in a clean `.venv`, started `uvicorn` on `127.0.0.1:8766` (automatic fallback around an occupied port `8765`), confirmed `401` on missing token, indexed all 8 `demo/` files, verified all 5 queries in `demo/queries.json` hit Rank 1 (`Recall@5 = 1.00`, `MRR = 1.00`, measured **1,425.9 ms total** via `eval/run_eval.py` over localhost HTTP), verified `private_*` exclusion purged `private_budget.txt`, confirmed pause refused scan with `409` and resume recovered cleanly, and confirmed `DELETE /index` zeroed search hits while leaving files intact on disk (`19 passed, 1 skipped` in `pytest` without semantic weights, plus `smoke OK`).
- **Pass 2 (Backup Plan — Wi-Fi Off / LAN Isolated):** Before Friday, run a second full walkthrough with desktop Wi-Fi toggled off and test Step 6 over a dedicated mobile hotspot (or keep Philip's 30-second screen recording queued in case campus Wi-Fi blocks peer-to-peer traffic).

---

## 4. Honest Limits (Mandatory Disclosure)

1. **Small Team-Written Eval Set:** Our evaluation corpus (`15` notes in `sample_lecture_notes/` and `8` files in `demo/`) was authored by the team, so Recall@5 (`1.00`) and MRR (`0.89` lenient keyword / `0.97` meaning & hybrid) are rough directional guides, not generalized benchmarks.
2. **Small-Quality Corpus vs. Synthetic Speed Timing:** `NFR1` keyword HTTP search passed `< 2.0 s` on **1,000 synthetic `.txt` files** ([`eval/time_search.py`](../eval/time_search.py): **median `0.0230 s`**, **max `0.0606 s`**, scan `10.24 s`, `n=20`), plus `3.49 ms` total (`0.23 ms/q`) direct FTS5 on 15 lecture notes, `1,425.9 ms` HTTP total on 5 `demo/` queries, and `412.8 ms/q` warm CPU query encoding on 63 chunks. However, the 1,000-file test uses repetitive synthetic `.txt` files (testing **speed only**, not real PDF/mixed retrieval quality or meaning-mode scale).
3. **Local Processing Is the Goal — Not "100% Private" or "Secure":** Files stay on the laptop in local keyword/embedding modes (`127.0.0.1` binding + token auth), but formal security penetration testing has not been performed.
4. **Local Index Is Unencrypted:** The SQLite database (`~/.sift/index.db`) is stored on disk in plaintext SQLite format without at-rest encryption. Any user or process with local OS read permissions to `$HOME/.sift` can read indexed snippets.
5. **Known Operational Gaps:** Experimental meaning mode ignores `ext`/`folder` filters, re-embeds at query time in the current prototype, and downloads ~90 MB of weights on the very first semantic query.
