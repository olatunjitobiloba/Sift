# Sift Architecture Decision Records (ADR)

---

## ADR 001: Local Agent Runtime & Language Selection (Python vs. Node.js)

**Date:** 2026-11-23  
**Status:** Accepted  
**Deciders:** Olatunji Oluwatobiloba (Product Owner / AI Lead), Sharon Bakare (Scrum Master), CPE434 Team 19  

### Context & Problem Statement
During Sprint 1, the team explored two implementations for the local desktop agent:
1. A Node.js prototype (`agent-node/`) using Express and `better-sqlite3`.
2. A Python service (`agent/app.py`) using FastAPI, SQLite with WAL mode, and `pypdf`.

With Sprint 2 introducing local semantic search (vector embeddings via `sentence-transformers`) and local audio transcription (`faster-whisper` quantized int8 models), having two competing codebases introduces technical debt and team confusion. A single language must be pinned for the local agent.

### Decision
The team selects **Python 3.10+ (FastAPI)** for the Sift local agent, while maintaining:
- **Node.js / Express** for the Cloud Relay & Pairing REST API.
- **React (Vite / TypeScript)** for the Web Dashboard.
- **React Native (Expo)** for the Mobile Companion App.

### Rationale
1. **Machine Learning & AI Ecosystem:** Local int8 audio transcription (`faster-whisper` / `CTranslate2`) and sentence embedding models (`all-MiniLM-L6-v2`) run natively in Python with direct C++/PyTorch bindings. Running these models in Node.js requires unmaintained ONNX wrappers or spawning external Python child processes, adding needless process orchestration overhead.
2. **Sprint 1 Investment & Hardening:** The Python agent is already hardened with 17 passing unit/integration tests, SQLite WAL mode, granular per-file commit lock relief on Windows, cooperative thread interruption on pause, timing-safe token authentication, and evaluation harnesses.
3. **Course & Department Approval:** Dr. Comfort Lawal confirmed that the web (React), mobile (Expo), and backend relay (Express) satisfy course requirements, permitting the local AI inference engine to run in Python.

### Consequences
- **Positive:** Maximum performance and lowest latency for local Whisper transcription and vector cosine similarity; clean separation between the heavy local inference engine (Python) and the lightweight client/relay tiers (TypeScript/JavaScript).
- **Negative:** Teammates working on the frontend must have a Python 3.10+ virtual environment on their machine to run the local agent during local end-to-end integration testing. Detailed setup commands and scripts are provided in `README.md` to mitigate this.
