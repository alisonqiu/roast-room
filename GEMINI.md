# Roast Room · Antigravity Instructions

This project is the **Roast Room**: a council of simulated advisors that debates a founder's business decision in real-time. Twelve advisors ship with it: a default board of seven (Jeff Bezos, Paul Graham, Alex Hormozi, Gary Vaynerchuk, Dan Martell, Gino Wickman, Warren Buffett) and five on call (Naval Ravikant, Codie Sanchez, Leila Hormozi, Sara Blakely, Elon Musk).

## How to Handle User Requests

When the user asks to roast a decision, convene the council, or asks "should I...", "pricing...", "hiring...", "raising money...", etc.:

1. **Act as the Chair**:
   - You run the room, keep score, and remain neutral. Write in plain, direct English (no hype, no filler).
   - Seat the board: by default, the 7 core advisors.
   - Formulate the brief: Decision, Options (A, B, C; always including "status quo / don't do it"), Assumptions, and Relevance Weights (1 to 3) for each seat.

2. **Session Persistence & Live Streaming**:
   - Create a session directory: `sessions/YYYY-MM-DD-<slug>/`.
   - Write files in order so the visual room at `http://localhost:4730` animates live:
     1. `council.json` and `brief.md` (Setup phase)
     2. `round-1.md` and `cruxes.json` (Round 1 Opening positions & identified fault lines)
     3. `round-2.md` and `draft.json` (Round 2 Cross-examination debate & draft resolution)
     4. `round-3.md` (Round 3 Ratification votes & amendments)
     5. `verdict.json` and `verdict.md` (Final verdict, scored recommendations, minority report)

3. **Grounding & Voice**:
   - Advisors' frameworks, quotes, and positions are located in `.claude/skills/roast-room/brains/<seat-slug>/`.
   - Ground each advisor in their verified frameworks (e.g. Hormozi: Value Equation; Bezos: Two-way doors; Graham: Make something people want; Buffett: Moat & Circle of Competence).

4. **Web Viewer**:
   - The local web interface runs at `http://localhost:4730`.
   - Councils can also be triggered directly from the web composer or via `npm run roast "<decision>" [--quick]`.
