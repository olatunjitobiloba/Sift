# Viva Notes — Olatunji Oluwatobiloba (Product Owner & Local Agent Lead)

## Five Lines Summary

1. **What I built:** The local Python/FastAPI agent ([`agent/app.py`](../../agent/app.py), [`agent/semantic.py`](../../agent/semantic.py)), SQLite FTS5 indexing with WAL mode, pause/exclusions lifecycle, token auth, [`demo/`](../../demo), the CI workflow ([`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)), and the evaluation benchmarks ([`eval/`](../../eval)).
2. **One decision and why:** Pinned Python for the local agent ([`docs/DECISIONS.md`](../DECISIONS.md) ADR 001/002) so `sentence-transformers` runs natively without Node child-process orchestration, and split heavy ML dependencies into [`agent/requirements-semantic.txt`](../../agent/requirements-semantic.txt) so CI runs in ~20 seconds.
3. **One bug and its fix:** `DELETE /folders` deleted sibling folders sharing a prefix (`/notes` wiping `/notes2`), fixed in [`remove_folder`](../../agent/app.py#L133-L142) by matching `p + os.sep` (`test_remove_folder_keeps_sibling`); also fixed a silent `8765` port collision with another local service returning `{"ok": true}` on `/health` by adding `"service": "sift-agent"` and falling back to `8766` in [`agent/smoke.py`](../../agent/smoke.py) and [`eval/run_eval.py`](../../eval/run_eval.py).
4. **One limit:** `NFR1` (`< 2 s` on 1,000 files) is still an unmeasured target, our eval corpus is small and team-written (15 files, 15 queries), local `index.db` is unencrypted plaintext SQLite on disk, and experimental `mode=meaning` re-embeds chunks per query and ignores `ext`/`folder` filters.
5. **What I'd change with another sprint:** Pre-compute and store chunk embeddings in SQLite at index time (during `do_scan`) rather than re-encoding all chunks on every semantic query, apply `ext`/`folder` filters inside meaning mode, and measure query latency on a real 1,000-file test folder.

---

## Defense Reference: Core Technical Questions

### 1. Why SQLite FTS5 + `bm25` instead of `LIKE '%q%'`?
- **Inverted Index Speed & Ranking:** `CREATE VIRTUAL TABLE chunks USING fts5(path UNINDEXED, text)` builds a token inverted index with built-in Okapi BM25 relevance scoring (`ORDER BY bm25(chunks)`, negated in Python because SQLite returns negative scores for best matches) and contextual snippet extraction (`snippet(chunks, 1, '[', ']', '...', 12)`). Plain `LIKE` forces a full table scan (`O(N)` text comparison), has no relevance ranking, and cannot highlight matching terms.
- **Measured Performance:** Direct SQLite FTS5 lenient-OR queries measured **3.49 ms total (0.23 ms/query)** across 15 queries on 63 chunks; over localhost HTTP on `demo/`, all 5 queries completed in **1,425.9 ms total** via `eval/run_eval.py`.
- **Syntax Safety:** User queries are split and double-quoted (`" ".join(f'"{t}"' for t in terms)`) so special symbols like `" OR * (` never break FTS5 query syntax (`test_odd_query_does_not_crash`).

### 2. Why `127.0.0.1` + `X-Sift-Token`, and what do they NOT protect against?
- **What they do:** Binding Uvicorn strictly to `127.0.0.1` keeps the HTTP API off LAN/Wi-Fi interfaces. Requiring `X-Sift-Token` validated with `secrets.compare_digest` prevents unauthenticated localhost browser tabs or scripts from reading indexed content (`test_token_required`, `test_no_token_is_401`).
- **What they do NOT protect against:** Any process running under the same OS user account can read `$HOME/.sift/token` or the unencrypted `$HOME/.sift/index.db` directly from disk; likewise, an allowed CORS origin (`localhost:5173`) given a valid token can query everything.

### 3. How does `remove_folder` protect sibling folders, and which test proves it?
- In [`agent/app.py`](../../agent/app.py#L133-L142), `remove_folder` resolves `p` and appends `os.sep` (`prefix = p + os.sep`) before matching `substr(path, 1, ?) = ?` across `chunks` and `files`. Because `/docs/notes/` does not prefix `/docs/notes2/`, sibling directories stay safe.
- Covered by **`test_remove_folder_keeps_sibling`** in [`agent/test_app.py`](../../agent/test_app.py#L136-L148).

### 4. How does Pause work, and why stop between files rather than mid-file?
- `POST /pause` sets `settings('paused', '1')`. `POST /scan` checks `is_paused(c)` and refuses new scans with HTTP `409` (`test_pause_blocks_scan`). Inside the background scan worker `do_scan()`, `if is_paused(c): break` runs at the top of the `for fp in files:` loop (`test_pause_mid_scan_halts`).
- Stopping cooperatively between file iterations avoids aborting threads mid-transaction or leaving half-indexed chunks for a document, while `c.commit()` at the end of each file releases the SQLite write lock so concurrent `/pause` or `/folders` requests do not fail with `database is locked` on Windows.

### 5. What did the embedding spike show? (Measured Numbers & Limits)
- Evaluated on 15 team-written engineering notes (63 chunks) with 15 conceptual memory queries ([`eval/SPIKE.md`](../../eval/SPIKE.md)):
  - **Keyword (Strict AND — agent default on multi-word memory queries):** `Recall@5 = 0.00`, `MRR = 0.00` (`0/15`).
  - **Keyword (Lenient OR):** `Recall@5 = 1.00`, `MRR = 0.89`, measured **3.49 ms total (0.23 ms/query)**.
  - **Meaning (`all-MiniLM-L6-v2`) & Hybrid (`RRF k=60`):** `Recall@5 = 1.00`, `MRR = 0.97` (`14/15` Rank 1 hits), measured **5.32 s** to encode chunks + **412.8 ms/query** warm query encode on CPU.
- **Caveats:** With only 15 queries written by the team, a single query swings the score (`1/15 = 0.067`), so small gaps count as noise and results are rough directional guides rather than broad proof. Keyword stays default (`test_default_mode_is_keyword`); meaning mode ships strictly as opt-in and experimental (`pytest.importorskip` skips it cleanly in fast CI runs).
