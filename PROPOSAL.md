# Sift: Product Proposal & Requirements Baseline

**Course:** CPE434 Computer Software Engineering I  
**Department:** Department of Electrical & Information Engineering, Covenant University  
**Milestone:** Week 4 Milestone Deliverable  
**Product:** Sift  
**Repository:** [https://github.com/olatunjitobiloba/Sift](https://github.com/olatunjitobiloba/Sift)  
**Project Board:** [https://github.com/users/olatunjitobiloba/projects/2](https://github.com/users/olatunjitobiloba/projects/2)  

---

## Section 1: Problem Definition & User Discovery

### 1.1 The Core Pain
Covenant University engineering students and faculty accumulate hundreds of unorganized lecture materials each semester—including voice recordings saved with arbitrary device names (`Voice 003.m4a`, `New Recording 12.aac`), multi-chapter textbook PDFs, and presentation slides (`Lecture_Week_4_final(2).pdf`). 

When preparing for tests, quizzes, or completing design projects, locating a specific theorem, circuit derivation, or lecturer explanation requires manually clicking through dozens of folders, skimming multiple PDF files, or listening through hours of audio recordings. Standard desktop operating system search (Windows Search / macOS Spotlight) relies heavily on matching file names or shallow metadata and fails completely on audio recordings or unscanned slide decks. Furthermore, while cloud AI tools (e.g. NotebookLM, ChatGPT) offer semantic search, students and researchers handling confidential project code, personal notes, or proprietary lab datasets face strict confidentiality and institutional privacy risks if raw files leave their devices.

### 1.2 User Interview Findings
To ground Sift in empirical evidence, the team conducted structured interviews with two undergraduate engineering students on their current study workflows and retrieval bottlenecks:

#### Interview 1: 400-Level Computer Engineering Student (Student A)
- **Current Setup:** Windows 11 laptop, ~600 lecture slide PDFs across 8 courses, 45 unnamed voice recordings in a generic WhatsApp voice note folder.
- **Observed Behavior:** Searching for "Amdahl's Law speedup formula" before a mid-semester test.
- **Pain Point:** Spent 22 minutes opening 7 different presentation slide decks. The term did not match Windows File Explorer search because the text was inside an image-embedded slide and the file was named `CPE411_Mod2_part3.pdf`.
- **Quote:** *"I know the lecturer explained the difference between strong and weak scaling in class, but I don't remember if it was Week 3 or Week 5, and listening to 3 hours of recordings is impossible when a test is tomorrow."*

#### Interview 2: 500-Level Electrical & Electronics Engineering Student (Student B)
- **Current Setup:** MacBook Air + Android phone, final-year design project notes, technical datasheets, personal budget spreadsheets.
- **Observed Behavior:** Managing project reference documentation and lecture notes.
- **Pain Point:** Reluctant to upload project datasets or personal documents to web-based AI tools due to privacy concerns and campus Wi-Fi data limits.
- **Quote:** *"I want an AI that can index my notes offline in the library without uploading my private drive or consuming my data bundle every time I search."*

---

## Section 2: User Archetypes

### Archetype 1: The Revision Sprinter (Undergraduate Student)
- **Persona:** Folajuwon, 400-Level Computer Engineering student.
- **Primary Goal:** Instantly find specific formulas, code snippets, or definitions across slides and lecture voice memos under tight exam preparation deadlines.
- **Current Workaround:** Asks classmates on WhatsApp groups ("Who has the slide on page tables?"), manually skimming through downloaded PDF files one by one.
- **Key Sift Value:** Sub-second keyword and semantic search over local lecture notes without needing to rename files.

### Archetype 2: The Privacy-Conscious Researcher
- **Persona:** Dr. Kemi, postgraduate researcher & teaching assistant.
- **Primary Goal:** Organize and query unpublished research drafts, laboratory test logs, and student project submissions without transmitting data to commercial cloud servers.
- **Current Workaround:** Grep/ripgrep in terminal or manual folder hierarchies; avoids cloud AI tools due to NDA and intellectual property restrictions.
- **Key Sift Value:** Guaranteed zero-egress local processing, folder-level exclusions, and verifiable index erasure.

### Archetype 3: The Multi-Device Campus Commuter
- **Persona:** David, 300-Level Information & Communication Engineering student.
- **Primary Goal:** Query notes from his phone while sitting in lecture halls or study labs while his laptop remains in the hostel room.
- **Current Workaround:** Emails files to himself or maintains messy duplicate folders on Google Drive.
- **Key Sift Value:** Remote phone-to-laptop query relay using short-lived one-time pairing codes without exposing raw file content to the cloud.

---

## Section 3: Initial Backlog & Requirements Traceability

### 3.1 Product Goal
> **Students and professionals can search their own lecture recordings, PDFs, slides, and notes by describing content and meaning—with all files, transcripts, and embeddings staying strictly on their laptop and under their control.**

### 3.2 User Stories & Active GitHub Issues Backlog
All user stories are maintained on GitHub Project Board #2 with INVEST-compliant Given–When–Then acceptance criteria.

| Story ID | User Story Title | Theme / Card | Traces to FRs | GitHub Issue |
|---|---|---|---|---|
| **1.1** | As a student, I want to choose which folders Sift indexes, so that only my study files are read | Card 1: Pick | FR1, FR2, FR3 | [#8](https://github.com/olatunjitobiloba/Sift/issues/8) |
| **1.2** | As a student, I want to exclude folders or file names, so that private files are never indexed | Card 1: Pick | FR4, FR5 | [#9](https://github.com/olatunjitobiloba/Sift/issues/9) |
| **2.1** | As a student, I want to search by a word I remember, so that I find a note without knowing its filename | Card 2: Find | FR6, FR7, FR8 | [#12](https://github.com/olatunjitobiloba/Sift/issues/12) |
| **2.2** | As a student, I want to filter results by file type, so that I can find a PDF or a text note quickly | Card 2: Find | FR9, FR10, FR11 | [#13](https://github.com/olatunjitobiloba/Sift/issues/13) |
| **3.1** | As a student, I want to pause indexing, so that Sift stops reading files when I choose | Card 3: Control | FR12 | [#10](https://github.com/olatunjitobiloba/Sift/issues/10) |
| **3.2** | As a student, I want to see and delete my index, so that I stay in control of my data | Card 3: Control | FR13 | [#14](https://github.com/olatunjitobiloba/Sift/issues/14) |
| **4.1** | As a student, I want to pair my phone with my laptop, so that I can search my notes away from my desk | Card 3: Control | FR14 | [#15](https://github.com/olatunjitobiloba/Sift/issues/15) |
| **4.2** | As a student, I want Sift to suggest where a file belongs and let me approve it, so that my folders get tidy without surprises *(Backlog — out of Sprint 2 / Demo scope)* | Card 3: Control | FR15 | [#11](https://github.com/olatunjitobiloba/Sift/issues/11) |

*(Detailed acceptance criteria and functional specifications are cataloged in [`docs/REQUIREMENTS.md`](./docs/REQUIREMENTS.md)).*

### 3.3 Measurable Non-Functional Requirements (ISO/IEC 25010)
1. **Performance Efficiency (Time Behaviour):** Search execution completes in under 2.0 seconds on a 1,000-file test corpus (`NFR1`; measured keyword HTTP search via `eval/time_search.py` on 1,000 synthetic `.txt` files: **median `0.0230s`**, **max `0.0606s`**; scan `10.24s`).
2. **Security (Authenticity & Access Control):** Every local agent HTTP request without a valid timing-safe token in `X-Sift-Token` receives HTTP 401 (`NFR2`, verified via `pytest agent/test_app.py::test_no_token_is_401`).
3. **Reliability (Fault Tolerance):** Pausing a running scan stops cleanly at file transaction boundaries, leaving the SQLite index uncorrupted and immediately searchable (`NFR3`, verified via `pytest agent/test_app.py`).
4. **Usability (Operability):** A newly onboarded student can add a folder and execute their first search without guidance in under 3 minutes (`NFR4`, target pending timed user trials).
5. **Security (Confidentiality & Local Processing):** The local agent binds exclusively to `127.0.0.1`, so document text stays on the host laptop by default (`NFR5`, verified via socket binding; note that local `index.db` storage is not encrypted at rest).

---

## Section 4: Team Roles & Ownership Roster

Following Scrum guidelines for CPE434, the team establishes distinct product and engineering ownership:

| Name | GitHub Handle | Scrum Role | Primary Technical Ownership |
|---|---|---|---|
| **Olatunji Oluwatobiloba** | `@olatunjitobiloba` | **Product Owner** & AI/ML Lead | Architecture governance, local Python agent core (`agent/app.py`), SQLite FTS5 search engine, Whisper transcription pipeline, and evaluation harness. |
| **Sharon Bakare** | `@milahg1` | **Scrum Master** & Frontend Lead | Sprint ceremony facilitation, React web dashboard (`web/`), folder management views, search result cards, pause/resume controls, and usability compliance. |
| **Philip** | `@Philips-Ay` | Developer (Mobile) | React Native / Expo mobile application, device pairing UI, mobile query views, and push notification listener. |
| **Elisha Oghweremu** | `@Elisha45` | Developer (Backend) | Cloud relay REST API (Node.js/Express), PostgreSQL metadata schemas (devices, audit logs), pairing code handshake, and Docker Compose configurations. |
| **Somto (Sergius Ede)** | `@SergiusE` | Developer (QA & DevOps) | Continuous Integration (GitHub Actions), baseline evaluation datasets (`eval/BASELINE.md`), end-to-end smoke testing, and security audits. |
