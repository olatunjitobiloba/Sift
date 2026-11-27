# Sift

> **Local-first, privacy-preserving document and lecture intelligence.**  
> Built for **CPE434: Computer Software Engineering I** · Department of Electrical and Information Engineering, Covenant University.

---

## 1. Product Goal
Students and professionals can search their own lecture recordings, PDFs, slides, and notes by describing content and meaning—with all files, transcripts, and embeddings staying strictly on their laptop and under their control.

---

## 2. Team Roster & Sprint 1 Roles
- **Olatunji Oluwatobiloba** (`@olatunjitobiloba`) — **Product Owner** & AI/ML Lead (Local Agent, Whisper Transcription, Embeddings, Search Pipeline)
- **Sharon Bakare** (`@milahg1`) — **Scrum Master** & Frontend Engineer (React Web & Local Dashboard)
- **Philip** (`@Philips-Ay`) — Developer: Mobile Engineer (React Native / Expo)
- **Elisha Oghweremu** (`@Elisha45`) — Developer: Backend Engineer (REST API, Relay Service & PostgreSQL Metadata)
- **Somto (Sergius)** (`@SergiusE`) — Developer: DevOps & QA Engineer (CI/CD, Security Audits, Jupyter Analytics & Docs)

*(See [`TEAM.md`](./TEAM.md) for full branch-contribution records and role rotations).*

---

## 3. High-Level Architecture & Privacy Boundary

```
LAPTOP (Strict Privacy Boundary — Zero Content Uploaded)
┌──────────────────────────────────────────────────────────────┐
│ Sift Local Agent (FastAPI / Java Core)                       │
│  - File Watcher (PDF, DOCX, Audio)                           │
│  - Local Transcription (faster-whisper int8)                │
│  - Local Embedding (all-MiniLM-L6-v2)                        │
│  - Local Search: SQLite FTS5 (BM25) + Vector RRF             │
│  - Move Journal & Undo Engine                                │
└──────────────────────────────┬───────────────────────────────┘
                               │ Outbound HTTPS Only (Polling)
                               ▼
CLOUD SERVICE (Metadata & Relay Only — No Raw Content)
┌──────────────────────────────────────────────────────────────┐
│ REST API (Express / Node.js or Java)                         │
│  - Device Pairing & Status                                   │
│  - Command Relay (Encrypted Payload Envelopes)               │
│  - PostgreSQL: Accounts, Devices, Audit Logs                 │
└──────────────────────────────┬───────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       React Web Dashboard            React Native (Expo)
    (Account & Device Control)      (Remote Find & Move Approval)
```

---

## 4. Repository Structure & Key Deliverables
- [`PLAN.md`](./PLAN.md) — CPE434 Week 2 Build Plan (Product, Incremental Process, Week 7 Increment, Tech Stack).
- [`SCRUM.md`](./SCRUM.md) — CPE434 Week 3 Scrum Charter (Sprint rhythm, WIP limits, Definition of Done).
- [`PROPOSAL.md`](./PROPOSAL.md) — CPE434 Week 4 Project Proposal (Problem definition, student interviews, archetypes, initial backlog, roles).
- [`docs/REQUIREMENTS.md`](./docs/REQUIREMENTS.md) — System Requirements Specification (Functional FR1–FR15, ISO/IEC 25010 NFR1–NFR5, User Story cards).
- [`docs/DECISIONS.md`](./docs/DECISIONS.md) — Architecture Decision Records (ADR 001: Local Agent Core Language).
- [`docs/CI.md`](./docs/CI.md) — Continuous Integration & Gatekeeping Specification (GitHub Actions workflow, branch protection).
- [`TEAM.md`](./TEAM.md) — Team collaboration log and individual branch verification.
- [`docs/DEMO.md`](./docs/DEMO.md) — 5-minute Week 13 demo script, Wi-Fi-off rehearsal checklist, and honest system limits.
- [`demo/`](./demo) — Synthetic 8-file sample study folder and 5-query verification suite.

---

## 5. Development & How to Run (Local Agent)

### Prerequisites
- Git
- Python **3.10+** (verified on Python 3.12 CI and Python 3.13 Windows)
- Node.js **18+ LTS** (for Web / Mobile / Cloud Relay)

### Quick Start (Fresh Clone)

1. **Clone the repository and enter `agent/`:**
   ```bash
   git clone https://github.com/olatunjitobiloba/Sift.git sift-fresh
   cd sift-fresh
   # Until PR #7 merges to main, check out feature/agent-skeleton:
   git checkout feature/agent-skeleton
   cd agent
   ```

2. **Create a virtual environment and install core dependencies** (takes ~5–15 seconds):
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\python.exe -m pip install -r requirements.txt
     ```
     *(Calling `.\.venv\Scripts\python.exe` directly avoids Windows PowerShell `ExecutionPolicy` blocks on `Activate.ps1`. Or activate normally with `.venv\Scripts\Activate.ps1`.)*
   - **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     ```

3. **Start the local agent (loopback `127.0.0.1` only):**
   - **Windows (PowerShell):**
     ```powershell
     .\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8765
     ```
   - **macOS / Linux:**
     ```bash
     uvicorn app:app --host 127.0.0.1 --port 8765
     ```
   *(If port `8765` is occupied on your machine, start with `--port 8766`; `smoke.py` falls back automatically from `8765` to `8766`.)*

4. **Verify health & grab your local API token** (created automatically on first agent startup in `~/.sift/token`):
   - **Windows (PowerShell):**
     ```powershell
     Invoke-RestMethod http://127.0.0.1:8765/health
     Get-Content $HOME\.sift\token
     ```
   - **macOS / Linux:**
     ```bash
     curl http://127.0.0.1:8765/health
     cat ~/.sift/token
     ```
   Pass that value in the `X-Sift-Token` HTTP header on all endpoints except `/health`.

5. **Run Unit Tests & End-to-End Smoke Test** (installs lightweight `pytest` + `httpx`):
   ```bash
   pip install -r requirements.txt pytest httpx
   pytest -q
   python smoke.py
   ```

6. **Optional: Enable Experimental Semantic / Hybrid Search (`mode=meaning` / `mode=hybrid`):**
   ```bash
   pip install -r requirements-semantic.txt
   ```
   - **First-run timing note:** Installing `sentence-transformers` downloads PyTorch and transformers (~150 MB+ wheels, ~1–3 min depending on connection). The very first semantic query (`?mode=meaning`) downloads `all-MiniLM-L6-v2` (~90 MB from Hugging Face) once into `~/.cache/huggingface/hub` and takes ~3–15 seconds depending on bandwidth. Subsequent runs work offline (~413 ms per warm query encode on CPU; note that the current experimental endpoint re-embeds chunks per query).
   - **Experimental status:** Keyword search remains the default (`mode=keyword`). Meaning mode currently ignores `ext` and `folder` filters.

7. **Run the Demo Dataset Rehearsal:**
   See [`docs/DEMO.md`](./docs/DEMO.md) and [`demo/queries.json`](./demo/queries.json). After launching the agent, evaluate the 5 known demo queries with:
   ```bash
   python ../eval/run_eval.py ../demo/queries.json
   ```
