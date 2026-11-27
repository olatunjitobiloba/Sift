# Sift Evidence & Readiness Audit (`docs/STATUS.md`)

**Last Updated:** 2026-11-27  
**Target Demo Date:** Friday, 4 December 2026  

Honest tracking of required evidence items. Items without complete verified proof remain explicitly marked **`not done`** until closed.

| Item | Status (`done` / `not done`) | Observed State & Proof (File or Link) |
|---|---|---|
| **CI green on `main`** | **not done** | PR [#7](https://github.com/olatunjitobiloba/Sift/pull/7) CI `test` job is green ([Run #46054562110](https://github.com/olatunjitobiloba/Sift/actions/runs/46054562110), 17s), and PR #16 proved broken tests block merges (RED). PR #7 still needs 1 teammate approval (`REVIEW_REQUIRED`) before merging into `main`. |
| **Eval: keyword vs meaning scores** | **done** | Recorded on 15 lecture notes / 15 human-memory queries in [`eval/SPIKE.md`](../eval/SPIKE.md) & [`eval/BASELINE.md`](../eval/BASELINE.md): Keyword strict AND MRR `0.00`, Keyword lenient OR MRR `0.89`, Embedding & Hybrid RRF (`k=60`) MRR `0.97`. |
| **2+ real student interviews** | **not done** | Draft discovery notes are in [`PROPOSAL.md`](../PROPOSAL.md), pending replacement/verification with verbatim weekend interviews (*"How do you find old lecture notes today?"*) from 2 real classmates. |
| **Dr Comfort's approval in writing** | **not done** | Verbal/relayed approval (`React, Expo, Express`) is recorded as ADR 002 in [`docs/DECISIONS.md`](./DECISIONS.md); written screenshot confirming Python local agent & weekly Java Swing labs is still pending. |
| **1,000-file search timing (`NFR1`)** | **done** | Measured live via [`eval/time_search.py`](../eval/time_search.py) on 2026-11-27 (1,000 synthetic `.txt` files, scan `10.24s`, `n=20` HTTP queries): **median `0.0230s`, max `0.0606s`** (Windows 11, i7-13620H). Logged in [`eval/BASELINE.md`](../eval/BASELINE.md) (speed only, not relevance quality). |
| **Fresh-clone test passed** | **not done (2nd machine)** | Passed locally on Toby's laptop (`feature/agent-skeleton` clone into temp `.venv`, `19 passed, 1 skipped`, `smoke OK`, `demo/` `MRR 1.00`), but not yet tested by a teammate on a second laptop from `main`. |

---

## Team Module Ownership Status (Add Your Evidence)

| Owner | Module / Evidence Task | Status | Target File |
|---|---|---|---|
| **Somto** | Confirm `main` CI green, branch protection screenshot, `docs/REQUIREMENTS.md` check | `not done` | [`docs/evidence/`](./evidence/README.md) |
| **Sharon** | UI accessibility & error states checklist + 5 viva lines | `not done` | `docs/UI-CHECK.md`, `docs/viva/sharon.md` |
| **Philip** | Mobile pairing demo recording + 5 viva lines | `not done` | `docs/viva/philip.md` |
| **Elisha** | Real `faster-whisper` transcription timing notes + 5 viva lines | `not done` | `docs/TRANSCRIPTION.md`, `docs/viva/elisha.md` |
| **Tobi** | Local agent, `NFR1` 1,000-file timing, ADR 001/002, CI, 5 viva lines | `done` *(pending PR #7 merge + Java email)* | [`docs/viva/tobi.md`](./viva/tobi.md), [`eval/BASELINE.md`](../eval/BASELINE.md) |
