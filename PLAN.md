# CPE434 Team Build Plan: Version 1

**Course**: CPE434 Computer Software Engineering I  
**Institution**: Covenant University, Department of Electrical & Information Engineering  
**Product**: Sift  
**Team**: Olatunji Oluwatobiloba, Sharon Bakare, Philip, Elisha, Somto  

---

### Box 1: Product and User
- **What we are building**: Sift, an AI-powered local-first file and lecture content intelligence engine. It transcribes audio recordings, parses documents (PDFs, DOCX, TXT), and enables semantic and keyword search directly on the user's laptop without uploading private files to third-party cloud servers.
- **For whom**: 
  1. *Primary*: Covenant University engineering students struggling to locate specific explanations across hundreds of unnamed audio recordings (`Recording (3).m4a`) and lecture slides.
  2. *Secondary*: Privacy-sensitive professionals, researchers, and accountants handling confidential files who cannot risk data leakage to external LLM providers.

---

### Box 2: Process Model
- **Chosen Model**: **Incremental Model** (with agile two-week sprint cadences).
- **Justification (one sentence)**: Student search workflows and local AI performance requirements evolve continuously through hands-on testing, so releasing working increments every 3 to 4 weeks ensures rapid feedback while keeping the critical indexing and privacy boundaries strictly verified on paper first.

---

### Box 3: First Increment (by Week 7)
Three tangible actions a user can perform in the first working version:
1. **Configure Scan Policies**: Opt-in to specific folders to index (e.g., `Documents/Lectures`) and specify exclude lists for sensitive personal directories.
2. **Execute Content-Based Search**: Search across indexed PDFs, text notes, and audio files by meaning/keywords and retrieve matching snippets with exact timestamps and page references.
3. **Inspect & Erase Index**: Inspect all indexed records transparently in a local UI and wipe the local index with a single click (verifiable with Wi-Fi disabled).

---

### Box 4: What We Will Reuse
- **Local Engine & AI**: Python / Java sidecar, `faster-whisper` (int8 quantized local transcription), `sentence-transformers` (`all-MiniLM-L6-v2` local embeddings), SQLite (FTS5 full-text search + vector extension).
- **Backend Service & Relay**: Node.js / Express (or Java REST API), PostgreSQL (user and device metadata only), Redis (command relay with short TTL).
- **Client Interfaces**: React (Web client & local dashboard), React Native with Expo (mobile client).
- **Analytics & Verification**: Python, Pandas, Jupyter Notebook (retrieval evaluation on golden test set), GitHub Actions (CI/CD pipeline, automated linting, test passes).
