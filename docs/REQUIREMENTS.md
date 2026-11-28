# Sift: System Requirements Specification

**Course:** CPE434 Computer Software Engineering I  
**Department:** Electrical & Information Engineering, Covenant University  
**Product:** Sift (Local-First Document & Lecture Intelligence Engine)  
**Standard:** ISO/IEC/IEEE 29148:2018 (Requirements Engineering) & ISO/IEC 25010 (System and Software Quality Models)  

---

## 1. Functional Requirements (FR)

Each functional requirement traces directly to a user story card and an active GitHub Issue.

| ID | Requirement Statement | Story Card | GitHub Issue |
|---|---|---|---|
| **FR1** | The system shall let a user add and remove folders to index | Story 1.1 (Card 1: Pick) | [#8](https://github.com/olatunjitobiloba/Sift/issues/8) |
| **FR2** | The system shall reject a path that is not a folder | Story 1.1 (Card 1: Pick) | [#8](https://github.com/olatunjitobiloba/Sift/issues/8) |
| **FR3** | The system shall index nothing until the user selects a folder | Story 1.1 (Card 1: Pick) | [#8](https://github.com/olatunjitobiloba/Sift/issues/8) |
| **FR4** | The system shall let a user exclude folders or file names | Story 1.2 (Card 1: Pick) | [#9](https://github.com/olatunjitobiloba/Sift/issues/9) |
| **FR5** | The system shall remove newly excluded files from the index on rescan | Story 1.2 (Card 1: Pick) | [#9](https://github.com/olatunjitobiloba/Sift/issues/9) |
| **FR6** | The system shall search indexed text by keyword and show a snippet | Story 2.1 (Card 2: Find) | [#12](https://github.com/olatunjitobiloba/Sift/issues/12) |
| **FR7** | The system shall show "No results" when nothing matches | Story 2.1 (Card 2: Find) | [#12](https://github.com/olatunjitobiloba/Sift/issues/12) |
| **FR8** | The system shall treat search text as plain text, not as raw query syntax | Story 2.1 (Card 2: Find) | [#12](https://github.com/olatunjitobiloba/Sift/issues/12) |
| **FR9** | The system shall filter results by file type (`.pdf`, `.txt`, `.md`) | Story 2.2 (Card 2: Find) | [#13](https://github.com/olatunjitobiloba/Sift/issues/13) |
| **FR10** | The system shall show each file once in results (deduplicating chunks) | Story 2.2 (Card 2: Find) | [#13](https://github.com/olatunjitobiloba/Sift/issues/13) |
| **FR11** | The system shall show "Agent not running" when the local agent is unreachable | Story 2.2 (Card 2: Find) | [#13](https://github.com/olatunjitobiloba/Sift/issues/13) |
| **FR12** | The system shall let a user pause and resume indexing gracefully | Story 3.1 (Card 3: Control) | [#10](https://github.com/olatunjitobiloba/Sift/issues/10) |
| **FR13** | The system shall let a user list indexed files and delete the index | Story 3.2 (Card 3: Control) | [#14](https://github.com/olatunjitobiloba/Sift/issues/14) |
| **FR14** | The system shall pair a phone with a one-time code | Story 4.1 / #7 (Card 3: Control) | [#15](https://github.com/olatunjitobiloba/Sift/issues/15) |
| **FR15** | The system shall move a file only after the user approves, with undo | Story 4.2 / #8 (Card 3: Control) | [#11](https://github.com/olatunjitobiloba/Sift/issues/11) |

---

## 2. Non-Functional Requirements (NFR)

All non-functional requirements are categorized according to **ISO/IEC 25010** software product quality characteristics with verifiable pass/fail metrics.

| ID | ISO/IEC 25010 Quality Sub-characteristic | Requirement Statement | Verification Method & Acceptance Metric |
|---|---|---|---|
| **NFR1** | **Performance Efficiency** (Time Behaviour) | Search query execution returns in under 2.0 seconds on a 1,000-file test folder (keyword FTS5 measured `median 0.0230s`, `max 0.0606s` on 1,000 synthetic `.txt` files). | [`eval/time_search.py`](../eval/time_search.py) timing 20 queries (`n=20`, 2026-11-27; speed only). |
| **NFR2** | **Security** (Authenticity & Access Control) | Every incoming HTTP request to the local agent without a valid timing-safe token in `X-Sift-Token` receives HTTP 401 Unauthorized. | Automated unit test suite (`pytest agent/test_app.py::test_no_token_is_401`). |
| **NFR3** | **Reliability** (Fault Tolerance & Integrity) | Pausing a running scan stops between file boundaries, leaves the SQLite index uncorrupted, and keeps existing entries immediately searchable. | Automated integration test (`pytest agent/test_app.py`). |
| **NFR4** | **Usability** (Learnability & Operability) | Target: a newly onboarded student adds a folder and executes their first search without external assistance in under 3 minutes. | Timed usability trial with 3 students; mean completion time <= 180s (pending measurement). |
| **NFR5** | **Security** (Local Processing Boundary) | The local search agent binds strictly to `127.0.0.1`, and file text stays on the host laptop by default (note: local SQLite index is unencrypted). | Check `--host 127.0.0.1` binding and offline demo rehearsal (Wi-Fi off). |

---

## 3. User Stories & Acceptance Criteria

Organized under the 3 core themes: **Pick**, **Find**, and **Control**. Acceptance criteria strictly adhere to the Given–When–Then tripartite pattern with **Happy**, **Edge**, and **Safe** verification cases.

### Card 1: Pick (Choose Folders & Exclusions)

#### Story 1.1: Folder Selection ([#8](https://github.com/olatunjitobiloba/Sift/issues/8))
> *As a student, I want to choose which folders Sift indexes, so that only my study files are read.*
1. **Happy:** Given I select a folder, when I confirm, then it appears in my folder list.
2. **Edge:** Given the path is not a folder, when I add it, then Sift shows an error and adds nothing.
3. **Safe:** Given I have not chosen a folder, when Sift runs, then it reads no files.

#### Story 1.2: Exclusion Rules ([#9](https://github.com/olatunjitobiloba/Sift/issues/9))
> *As a student, I want to exclude folders or file names, so that private files are never indexed.*
1. **Happy:** Given I add an exclusion, when I scan, then matching files are not indexed.
2. **Edge:** Given the pattern is empty, when I save it, then it is rejected.
3. **Safe:** Given a file was indexed before, when I exclude it and rescan, then it is removed from the index.

---

### Card 2: Find (Search & Filter)

#### Story 2.1: Keyword Search ([#12](https://github.com/olatunjitobiloba/Sift/issues/12))
> *As a student, I want to search by a word I remember, so that I find a note without knowing its filename.*
1. **Happy:** Given indexed files, when I search "deadlock", then matching files show with a snippet.
2. **Edge:** Given no file matches, when I search, then I see "No results", not an error.
3. **Safe:** Given I type symbols like `" OR *`, when I search, then the app does not crash.

#### Story 2.2: File-Type Filtering ([#13](https://github.com/olatunjitobiloba/Sift/issues/13))
> *As a student, I want to filter results by file type, so that I can find a PDF or a text note quickly.*
1. **Happy:** Given I pick "PDF", when I search, then only PDFs appear.
2. **Edge:** Given a file has several matches, when results show, then it appears once.
3. **Safe:** Given the agent is off, when I search, then the UI says "Agent not running".

---

### Card 3: Control (Privacy, Lifecycle & Extensions)

#### Story 3.1: Scan Pausing ([#10](https://github.com/olatunjitobiloba/Sift/issues/10))
> *As a student, I want to pause indexing, so that Sift stops reading files when I choose.*
1. **Happy:** Given I press Pause, when I start a scan, then it is refused.
2. **Edge:** Given a scan is running, when I press Pause, then it stops between files.
3. **Safe:** Given I press Resume, when I scan again, then it continues normally.

#### Story 3.2: Transparency & Index Deletion ([#14](https://github.com/olatunjitobiloba/Sift/issues/14))
> *As a student, I want to see and delete my index, so that I stay in control of my data.*
1. **Happy:** Given files are indexed, when I open "Indexed files", then I see the list.
2. **Edge:** Given I delete a file from disk, when I rescan, then it leaves the index.
3. **Safe:** Given I click "Delete index", when I search, then I get zero results.

#### Story 4.1 (Issue #7): Mobile Device Pairing ([#15](https://github.com/olatunjitobiloba/Sift/issues/15))
> *As a student, I want to pair my phone with my laptop, so that I can search my notes away from my desk.*
1. **Happy:** Given the agent is running, when I open "Pair phone", then a one-time code appears.
2. **Edge:** Given I enter a wrong or expired code, when I submit, then pairing is refused and no device is added.

#### Story 4.2 (Issue #8 — Backlog): Human-in-the-Loop File Organization ([#11](https://github.com/olatunjitobiloba/Sift/issues/11))
> *Status: **Backlog** (Deferred from Sprint 2 and Week 13 demo scope).*
> *As a student, I want Sift to suggest where a file belongs and let me approve it, so that my folders get tidy without surprises.*
1. **Happy:** Given a suggestion exists, when I click Approve, then only that file moves, and I can undo it.
2. **Edge:** Given I do not approve, when time passes, then no file is moved.
