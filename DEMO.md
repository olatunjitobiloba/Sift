# Sift Sprint 1 Demo Script (5 Minutes)

**Presentation Guidance**: Say *"search runs on your laptop."* Do not say *"100% private."*

---

### 1. Problem (30s)
- **Pitch**: "Where did I save that lecture note?"
- Show the problem students face: hundreds of unnamed or vaguely titled notes and slides (`Lecture_2_final.pdf`, `circuits_notes.txt`). Locating a specific concept across slides usually means opening every file one by one.

---

### 2. Consent & Privacy Controls (45s)
- **Folder Picker**: Add an opt-in folder (`sample_lecture_notes`).
- **Exclusions**: Show the exclusion list (e.g. `Private` or `*.secret`). Explain that exclusions run at scan time so private documents are never parsed or stored in SQLite.
- **Pause Toggle**: Demonstrate pausing indexing.

---

### 3. Search & Filtering (60s)
- Search for a technical concept (e.g. `Thevenin`).
- Show instant SQLite FTS5 BM25 keyword matching with contextual snippets and file paths.
- Demonstrate file-type filters: filter by `.txt` or `.pdf`.
- Highlight deduplication: exactly one card per document displaying its highest-ranking passage.

---

### 4. Control & Data Deletion (45s)
- Trigger one-click index deletion (`DELETE /index`).
- Re-run the search query: search returns zero hits immediately.
- Explain: user files are left intact on disk, but the local inverted index is purged.

---

### 5. Mobile Interface (45s)
- Present Philip's React Native (Expo) app running on a mobile device.
- Show device pairing screen and search result view (or the 30-second backup video).

---

### 6. Benchmark Evidence (45s)
- Show the evaluation benchmark from `eval/BASELINE.md`.
- Report **Recall@5** and **MRR (Mean Reciprocal Rank)** on the 20-file evaluation suite.
- State clearly: this gives the team a numerical baseline to measure semantic search against in Sprint 2.

---

### 7. Next Steps (30s)
- Conclude: Sprint 1 established the local agent, non-blocking indexing, and privacy controls.
- Sprint 2 target: local `faster-whisper` transcription for lecture recordings and vector embeddings for semantic search.
