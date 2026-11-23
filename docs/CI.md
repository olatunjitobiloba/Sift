# Sift Continuous Integration & Gatekeeping Specification

**Course:** CPE434 Computer Software Engineering I  
**Milestone:** Week 11 CI Milestone  
**Pipeline File:** [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)  
**Status Gate:** Mandatory for all Pull Requests targeting `main`  

---

## 1. CI Pipeline Architecture

The Sift CI workflow is triggered automatically on:
- Every push to the `main` branch.
- Every Pull Request targeting `main`.

```
GitHub Actions Runner (ubuntu-latest)
┌─────────────────────────────────────────────────────────────┐
│ 1. actions/checkout@v4                                      │
│ 2. actions/setup-python@v5 (Python 3.12 + pip cache)       │
│ 3. pip install -r agent/requirements.txt pytest httpx      │
│ 4. Unit Tests: pytest -q (All unit and auth tests)         │
│ 5. Smoke Test: Background uvicorn daemon + smoke.py        │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
        PASS (Green)                          FAIL (Red)
     PR Merge Permitted                    Merge Blocked
```

---

## 2. Coverage Scope

### What CI Covers:
- **Fast Clean Installation:** Uses lightweight `agent/requirements.txt` (FastAPI, Uvicorn, PyPDF) to ensure builds execute in under 30 seconds.
- **Unit Test Verification:** Runs the complete unit test suite (`pytest -q`), including token authentication checks (`NFR2: test_no_token_is_401`), folder prefix collision guards, and search deduplication.
- **Live Background Daemon Smoke Test:** Spawns a background `uvicorn app:app` process on `127.0.0.1:8765`, polls `/health` for readiness, reads `$SIFT_HOME/token`, and runs `smoke.py` end-to-end (folder creation, background scan telemetry, and search retrieval).
- **Merge Gatekeeping:** With branch protection enabled, pull requests cannot be merged into `main` if the `test` job fails.

### What CI Does Not Cover (Known Gaps & Future Work):
- **Operating System Environment:** CI runs on Ubuntu Linux (`ubuntu-latest`). Windows-specific path behaviors (e.g. backslash `os.sep` and Windows SQLite file lock handling) are tested locally on Windows 11.
- **Heavy Embedding Models:** Heavy machine learning dependencies (`sentence-transformers`, PyTorch) are isolated in `agent/requirements-semantic.txt`. Tests requiring embeddings use `pytest.importorskip("sentence_transformers")` to skip gracefully in CI without failing or downloading ~130 MB of weights.
- **Cloud Relay & Docker Compose:** The Express/PostgreSQL relay service Docker build is tracked separately by Elisha.
- **Frontend Web & Mobile Builds:** React/Vite (`web/`) and React Native Expo (`mobile/`) linting/type-checking jobs will be integrated as parallel CI matrix jobs once their respective PRs land.

---

## 3. Branch Protection Policy

To guarantee that broken code never reaches `main`, the following rules are enforced on the repository:
1. **Require a pull request before merging:** Direct pushes to `main` are blocked.
2. **Require status checks to pass before merging:** The `test` job from `.github/workflows/ci.yml` must succeed.
3. **Require approvals:** At least 1 peer review approval from a team member.
4. **Do not allow bypassing the above settings:** Enforced for all contributors.
