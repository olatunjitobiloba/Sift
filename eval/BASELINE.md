# Sift Evaluation Benchmark Baseline

**Dataset:** 15 Covenant University Engineering lecture notes (`sample_lecture_notes/`, 63 chunks)  
**Queries:** 15 student revision memory queries (`eval/queries.json`)  

---

## Milestone Progress Track

| Milestone / Sprint | Date | Search Mode Evaluated | Recall@5 | MRR | Latency / Throughput | Status |
|---|:---:|---|:---:|:---:|:---:|:---:|
| **Sprint 1 Baseline** | 2026-11-23 | Keyword FTS5 BM25 (lenient OR) | **1.00** | **0.89** | 4.2 ms total | Baseline Established |
| **Sprint 2 Spike** | 2026-11-23 | Semantic (`all-MiniLM-L6-v2`) | **1.00** | **0.97** | 19.3 chunks/s | Verified Improvement |
| **Sprint 2 Spike** | 2026-11-23 | Hybrid (RRF, $k=60$) | **1.00** | **0.97** | ~16 ms per query | Recommended Target |
| **Week 10 Increment** | 2026-11-23 | Agent `/search?mode=meaning` & `mode=hybrid` | **1.00** | **0.97** | Lazy-loaded on CPU | **Shipped in `agent/app.py`** |

---

## Baseline Benchmark Results (Sprint 1)

| Metric | Score | Target | Status |
|---|:---:|:---:|---|
| **Recall@5** | **1.00** (15/15) | $\ge$ 0.80 | Pass |
| **MRR (Mean Reciprocal Rank)** | **0.89** | $\ge$ 0.70 | Pass |
| **Total Query Latency (15 queries)** | **4.2 ms** | < 200 ms | Pass (Sub-millisecond per query) |

### Per-Query Breakdown (FTS5 BM25)

| Query | Expected Note | FTS5 Rank | Status |
|---|---|:---:|---|
| "tasks frozen in infinite sleep waiting for locks" | `CPE421_Operating_Systems_Deadlocks.txt` | Rank 1 | Hit |
| "eliminating duplicate columns across entities in relational storage" | `CPE414_Database_Management_Normalization.txt` | Rank 1 | Hit |
| "preventing CPU execution delays between consecutive instructions" | `CPE411_Microprocessor_Instruction_Pipelining.txt` | Rank 1 | Hit |
| "how a diode stops electric current until threshold voltage is reached" | `PHY121_Semiconductor_Physics.txt` | Rank 3 | Hit |
| "turning a complex linear circuit into a single battery and resistor" | `EIE411_Thevenin_Theorem.txt` | Rank 1 | Hit |
| "preventing sender from overwhelming the destination buffer" | `CPE412_Computer_Networks_OSI_TCP.txt` | Rank 1 | Hit |
| "rapid spectral frequency decomposition from time samples" | `EIE423_Digital_Signal_Processing_FFT.txt` | Rank 1 | Hit |
| "tuning feedback controller loops using critical oscillation period" | `EIE413_Control_Systems_PID_Tuning.txt` | Rank 1 | Hit |
| "constructing hierarchical trees from lexical tokens using grammar rules" | `CPE432_Compiler_Construction_Syntax_Analysis.txt` | Rank 1 | Hit |
| "microcontroller bus using two wires with pullup resistors" | `CPE422_Embedded_Systems_Interfacing.txt` | Rank 2 | Hit |
| "equations relating electric displacement and circulating magnetic induction" | `EIE425_Electromagnetic_Fields_Maxwell_Equations.txt` | Rank 1 | Hit |
| "ciphers based on the difficulty of factoring very large prime numbers" | `CPE436_Information_Security_Cryptography.txt` | Rank 1 | Hit |
| "numerical convergence methods for bus voltages in electrical networks" | `EIE415_Power_Systems_Load_Flow_Analysis.txt` | Rank 1 | Hit |
| "simulating shiny glossy reflections using viewing angles and light vectors" | `CPE424_Computer_Graphics_Rendering_Pipeline.txt` | Rank 2 | Hit |
| "ten minute daily team standup to remove project roadblocks" | `CPE434_Software_Engineering_Agile.md` | Rank 1 | Hit |

### Known Limitations
- When student memory queries use descriptive conceptual terms rather than technical jargon, keyword BM25 drops in rank precision (e.g. diode barrier potential dropped to Rank 3, pullup resistors dropped to Rank 2, Phong reflection dropped to Rank 2). Embeddings and Hybrid search resolve this limitation by lifting MRR from 0.89 to 0.97.
