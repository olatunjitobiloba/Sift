# Sprint 2 Research Spike: Keyword vs. Embedding vs. Hybrid Search

**Date:** 2026-11-23  
**Author:** Olatunji Oluwatobiloba (Product Owner & AI Lead)  
**Corpus:** 15 Covenant University Engineering lecture notes (63 paragraph chunks in `sample_lecture_notes/`)  
**Evaluation Set:** 15 human-memory conceptual queries (`eval/queries.json`)  
**Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors, normalized dot product)  
**Fusion Method:** Reciprocal Rank Fusion (RRF) with constant $k = 60$  

---

## 1. 3-Way Comparative Benchmark

| Search Method | Retrieval Mechanism | Recall@5 | MRR (Mean Reciprocal Rank) | Rank 1 Exact Hits | Notes |
|---|---|:---:|:---:|:---:|---|
| **Keyword (Strict AND)** | SQLite FTS5 BM25 (`"term1" "term2"`) | **0.00** | **0.00** | 0 / 15 (0%) | Current agent behavior: all terms required; natural memory queries miss due to missing words. |
| **Keyword (Lenient OR)** | SQLite FTS5 BM25 (`"term1" OR "term2"`) | **1.00** | **0.89** | 11 / 15 (73.3%) | Measured 0.23 ms/query; matches vocabulary overlap but precision drops on descriptive phrases. |
| **Embedding (Semantic)** | `all-MiniLM-L6-v2` Cosine Similarity | **1.00** | **0.97** | **14 / 15 (93.3%)** | Measured 412.8 ms/query (warm query encode) + 5.32 s corpus encode on CPU. |
| **Hybrid (RRF, $k=60$)** | Keyword + Embedding Fusion | **1.00** | **0.97** | **14 / 15 (93.3%)** | Combines lexical exactness with semantic understanding (~413 ms warm query CPU). |

---

## 2. Decision Rule Application

According to the Sprint 2 Planning Decision Framework:

| Decision Rule Condition | Action | Applied? |
|---|---|:---:|
| **Hybrid beats keyword by a clear margin** | Pull **"Hybrid search"** card into Sprint 2 | **YES (MRR 0.97 vs 0.89 / 0.00)** |
| Embeddings and hybrid are about equal to keyword | Keep keyword, spend sprint on transcription & UX | No |
| Keyword wins | Drop embeddings for now | No |

### Formal Decision:
**We commit the "Hybrid search" card to Sprint 2.**  
Hybrid search with Reciprocal Rank Fusion ($k=60$) resolves the fatal flaw of keyword search (where queries fail when a student forgets exact wording) while preserving the ability of SQLite FTS5 to match exact course codes (`EIE411`, `CPE434`), technical acronyms (`FFT`, `TCP`, `PID`, `UART`, `BCNF`), and formulas.

---

## 3. Query-by-Query Comparison

| # | Benchmark Query | Expected Target File | Keyword (AND) | Keyword (OR) | Embedding | Hybrid (RRF) |
|---|---|---|:---:|:---:|:---:|:---:|
| 1 | "tasks frozen in infinite sleep waiting for locks" | `CPE421_Operating_Systems_Deadlocks.txt` | MISS | Rank 1 | **Rank 1** | **Rank 1** |
| 2 | "eliminating duplicate columns across entities in relational storage" | `CPE414_Database_Management_Normalization.txt` | MISS | Rank 1 | **Rank 1** | **Rank 1** |
| 3 | "preventing CPU execution delays between consecutive instructions" | `CPE411_Microprocessor_Instruction_Pipelining.txt` | MISS | Rank 1 | Rank 2 | Rank 2 |
| 4 | "how a diode stops electric current until threshold voltage is reached" | `PHY121_Semiconductor_Physics.txt` | MISS | Rank 3 | **Rank 1** | **Rank 1** |
| 5 | "turning a complex linear circuit into a single battery and resistor" | `EIE411_Thevenin_Theorem.txt` | MISS | Rank 1 | **Rank 1** | **Rank 1** |
| 6 | "preventing sender from overwhelming the destination buffer" | `CPE412_Computer_Networks_OSI_TCP.txt` | MISS | Rank 1 | **Rank 1** | **Rank 1** |
| 7 | "rapid spectral frequency decomposition from time samples" | `EIE423_Digital_Signal_Processing_FFT.txt` | MISS | Rank 1 | **Rank 1** | **Rank 1** |
| 8 | "tuning feedback controller loops using critical oscillation period" | `EIE413_Control_Systems_PID_Tuning.txt` | MISS | Rank 1 | **Rank 1** | **Rank 1** |
| 9 | "constructing hierarchical trees from lexical tokens using grammar rules" | `CPE432_Compiler_Construction_Syntax_Analysis.txt` | MISS | Rank 1 | **Rank 1** | **Rank 1** |
| 10 | "microcontroller bus using two wires with pullup resistors" | `CPE422_Embedded_Systems_Interfacing.txt` | MISS | Rank 2 | **Rank 1** | **Rank 1** |
| 11 | "equations relating electric displacement and circulating magnetic induction" | `EIE425_Electromagnetic_Fields_Maxwell_Equations.txt` | MISS | Rank 1 | **Rank 1** | **Rank 1** |
| 12 | "ciphers based on the difficulty of factoring very large prime numbers" | `CPE436_Information_Security_Cryptography.txt` | MISS | Rank 1 | **Rank 1** | **Rank 1** |
| 13 | "numerical convergence methods for bus voltages in electrical networks" | `EIE415_Power_Systems_Load_Flow_Analysis.txt` | MISS | Rank 1 | **Rank 1** | **Rank 1** |
| 14 | "simulating shiny glossy reflections using viewing angles and light vectors" | `CPE424_Computer_Graphics_Rendering_Pipeline.txt` | MISS | Rank 2 | **Rank 1** | **Rank 1** |
| 15 | "ten minute daily team standup to remove project roadblocks" | `CPE434_Software_Engineering_Agile.md` | MISS | Rank 1 | **Rank 1** | **Rank 1** |

---

## 4. Measured Performance & Caveats

- **Corpus Embedding Time:** 63 chunks embedded in **3.27–5.32 s** on laptop CPU (`all-MiniLM-L6-v2`, batch size 32).
- **Measured Query Latency (15 queries, 63 chunks):**
  - Keyword FTS5 (lenient OR): **3.49 ms total (0.23 ms/query)**
  - Warm Semantic Query Encoding (`model.encode` + dot product): **6,191.65 ms total (412.78 ms/query)** on laptop CPU.
  - Note: In the Week 10 experimental `/search?mode=meaning` endpoint, all chunks are currently re-encoded on each query; indexing embeddings to SQLite at scan time is required to scale beyond small folders.
- **Caveats & Unmeasured Targets:**
  - The 15-note eval set is small and team-authored, so Recall@5 and MRR are rough directional guides.
  - `NFR1` (`< 2.0 s` on 1,000 files) remains a target and has not been benchmarked at 1,000 files.
- **Disk Overhead**: `all-MiniLM-L6-v2` model weights require ~90 MB on disk (cached once under `~/.cache/huggingface/hub`). Vector indices require 1.5 KB per paragraph chunk (384 float32 values).

---

## 5. Audio Transcription Spike (Elisha's Section)

*To be updated by Elisha (`@Elisha45`):*
- **Model:** `faster-whisper` (`small` model, int8 quantization via CTranslate2).
- **Audio Duration:** 10.0 minutes of recorded lecture audio.
- **Elapsed Transcription Time:** *(Awaiting Elisha's benchmark)*.
- **Real-Time Factor (RTF):** *(Elapsed / Duration)*.
- **10 Noted Word Errors / Technical Vocabulary Drops:**
  1. 
  2. 
  3. 
  4. 
  5. 
  6. 
  7. 
  8. 
  9. 
  10. 
