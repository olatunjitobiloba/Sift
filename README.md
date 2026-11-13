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
- [`TEAM.md`](./TEAM.md) — Team collaboration log and individual branch verification.

---

## 5. Development & How to Run
*(Instructions will be updated as each module increments pass the Definition of Done).*

### Prerequisites
- Git & GitHub
- Java JDK 17+ / Python 3.10+ / Node.js LTS
- VS Code

```bash
# Clone the repository
git clone https://github.com/olatunjitobiloba/Sift.git
cd Sift

# Switch to your feature branch before writing code
git switch -c feature/<your-task-name>
```
