# Scrum Charter: Sift

## 1. Product Goal
Students and professionals can search their own lecture files and documents by describing the content, with all file data staying on their laptop and under their control.

---

## 2. Roles for Sprint 1 (Weeks 3–5)
*(Roles rotate each sprint as required by the course syllabus)*

- **Product Owner**: Sharon Bakare (Owns requirements, user stories, acceptance criteria, and stakeholder communication)
- **Scrum Master**: Somto (Facilitates sprint rhythm, enforces WIP limits, unblocks teammates, monitors DoD compliance)
- **Developers**:
  - **Olatunji Oluwatobiloba**: AI/ML Lead (Local Agent, Whisper transcription, embedding pipeline, SQLite FTS5/vector indexing)
  - **Elisha**: Backend Engineer (REST API service, device management, command relay, PostgreSQL metadata)
  - **Philip**: Mobile Engineer (React Native / Expo mobile client, device pairing, remote command triggers)
  - **Sharon Bakare**: Frontend Engineer (React web dashboard and local UI controls)

---

## 3. Rhythm
- **Sprint Length**: 2 weeks
- **Daily Scrum**: Monday, Wednesday, Friday at 19:30 WAT (10 minutes, remote/stand-up: what I did, what I will do, blockers)
- **Sprint Planning**: Alternate Mondays at 19:00 WAT (30 minutes)
- **Sprint Review**: In the CPE434 laboratory session with course assistants / lecturer
- **Sprint Retrospective**: Following the review (15 minutes: what went well, what broke, what we improve)

---

## 4. Work In Progress (WIP) Limits
- **In Progress limit**: **5 cards maximum** (strictly 1 active task card per developer at any given time to eliminate context switching and unfinished PRs).
- **In Review limit**: 3 cards maximum.

---

## 5. Definition of Done (DoD)
A card cannot be moved to **Done** on the GitHub Projects board unless all five conditions are satisfied:

- [ ] **Compiles and runs**: Code compiles cleanly and passes all local tests on a teammate's machine.
- [ ] **Branch discipline**: Built on a descriptive feature branch (`feature/<name>-<task>`), merged only through a Pull Request (never pushed directly to `main`).
- [ ] **Peer review**: At least one designated teammate has reviewed, tested, and approved the Pull Request.
- [ ] **Acceptance checks**: Meets the exact acceptance criteria defined in the user story card.
- [ ] **Documentation**: `README.md` or component docs clearly describe how to configure and run the changes.
- [ ] **AI tool disclosure**: The pull request description explicitly names any AI coding tool used and confirms the author can explain every line.
