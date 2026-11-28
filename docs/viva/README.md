# Viva Preparation Notes (`docs/viva/`)

Each team member writes **5 lines** on their own work in `docs/viva/<name>.md`:
1. **What I built:** The specific modules, routes, or screens you authored.
2. **One decision and why:** An architecture or tooling tradeoff you made.
3. **One bug and its fix:** A real defect you found and the regression test or commit that fixed it.
4. **One limit:** What your module cannot do yet (be specific; no vague claims).
5. **What I'd change:** One concrete improvement given another sprint.

## Expected Files
- [`tobi.md`](./tobi.md) — Olatunji Oluwatobiloba (Local Agent, Search Engine, Evaluation, CI)
- `sharon.md` — Sharon Bakare (Web UI, Dashboard, Error States, Accessibility)
- `somto.md` — Somto / Sergius Ede (Evaluation Set, CI Gatekeeping, Docs Verification)
- `philip.md` — Philip (Expo Mobile App, Device Pairing, Search Flow)
- `elisha.md` — Elisha Oghweremu (Cloud Relay API, Docker Compose, Whisper Timing Spike)

## Mock Viva Drill (20–30 Minutes)
Pair up across the team. One teammate opens a random file from the repo and asks the author:
1. What does this file do?
2. Why was it written this way instead of the simpler alternative?
3. What breaks if I delete this file?
4. Which automated test proves this works?

**Answer Rules for the Panel:**
- Say *"I don't know, but here is how I would check"* rather than guessing.
- Separate **measured numbers** from **targets**.
- Say *"local-first by design"* (and note `index.db` is unencrypted); avoid *"100% private"* or *"secure."*
- Point directly to commits (`git log`) to show individual ownership.
