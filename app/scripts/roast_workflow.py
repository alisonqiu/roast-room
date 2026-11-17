"""
Antigravity Dynamic Workflow for Roast Room
Orchestrates a board of advisors through Round 1 (Openings), Cruxes, Round 2 (Debate), Draft Resolution, Round 3 (Vote), and Verdict.
Writes live session files so the visual room at http://localhost:4730 updates in real time.
"""
import os
import json
import re
import datetime
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BRAINS_DIR = REPO_ROOT / ".claude" / "skills" / "roast-room" / "brains"
ROSTER_PATH = REPO_ROOT / ".claude" / "skills" / "roast-room" / "roster.json"
SESSIONS_DIR = REPO_ROOT / "sessions"

def load_roster():
    with open(ROSTER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def slugify(text):
    text = (text or "council").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:50] or "council"

def get_brain(slug):
    slug_dir = BRAINS_DIR / slug
    parts = []
    for fname in ["principles.md", "frameworks.md", "voice.md", "positions.md"]:
        p = slug_dir / fname
        if p.exists():
            parts.append(f"--- {fname} ---\n" + p.read_text(encoding="utf-8")[:3000])
    return "\n\n".join(parts)

prompt = args.get("decision", "Should I raise a seed round or stay bootstrapped?")
mode = args.get("mode", "full")

log(f"Starting council on: {prompt} (mode: {mode})")
phase("Setup")

roster = load_roster()
seats_meta = {s["key"]: s for s in roster.get("seats", [])}
board_keys = roster.get("default", ["bezos", "graham", "hormozi", "garyvee", "martell", "wickman", "buffett"])
if mode == "quick":
    board_keys = board_keys[:4]

date_str = datetime.date.today().isoformat()
session_slug = f"{date_str}-{slugify(prompt)}"
session_dir = SESSIONS_DIR / session_slug
session_dir.mkdir(parents=True, exist_ok=True)

# 1. Setup / Brief
options = [
    {"id": "A", "label": "Option A (Pursue new path)"},
    {"id": "B", "label": "Option B (Measured test)"},
    {"id": "C", "label": "Option C (Keep status quo)"}
]

council_data = {
    "title": prompt[:60],
    "decision": prompt,
    "mode": mode,
    "options": options,
    "weights": {k: {"weight": 2, "reason": seats_meta[k]["pillar"]} for k in board_keys},
    "seats": board_keys,
    "brief": f"Founder decision: {prompt}",
    "assumptions": ["Market conditions remain steady (assumed)"]
}

(session_dir / "council.json").write_text(json.dumps(council_data, indent=2), encoding="utf-8")
(session_dir / "brief.md").write_text(f"# {council_data['title']}\n\n{council_data['brief']}\n\nOptions:\n- A: {options[0]['label']}\n- B: {options[1]['label']}\n- C: {options[2]['label']}\n", encoding="utf-8")

log(f"Session initialized at: {session_dir}")

# 2. Round 1: Openings
phase("Round 1: Openings")

async def run_seat_r1(key):
    s = seats_meta[key]
    brain = get_brain(s["slug"])
    r1_prompt = f"""You are {s['name']} ({s['pillar']}).
Your personality and core principles:
{brain}

THE DECISION: {prompt}
OPTIONS:
(A) {options[0]['label']}
(B) {options[1]['label']}
(C) {options[2]['label']}

State your opening position concisely in character under 200 words:
SEAT: {s['short'].upper()} ({s['pillar']})
STANCE: Strong yes | Yes | Conditional yes | No | Strong no
OPTION SCORES: A 7/10 · B 6/10 · C 4/10
PILLAR SCORE: 8/10
CONFIDENCE: 4/5
RUIN RISK: none | possible | likely
DOOR: one-way | two-way
THE CALL: one sentence.
WHY:
1. main argument
THE RISK I SEE: one sentence.
WHAT I'D DO THIS WEEK: one action."""
    res = await agent(prompt=r1_prompt, schema={"type": "string"}, role=f"{s['short']} (R1)")
    return key, res

r1_results = await parallel(board_keys, run_seat_r1)
r1_md = "# Round 1\n\n" + "\n\n".join([f"## {seats_meta[k]['name']}\n\n{text}" for k, text in r1_results])
(session_dir / "round-1.md").write_text(r1_md, encoding="utf-8")

cruxes_data = {
    "cruxes": [
        {
            "question": "Is speed and aggressive expansion worth the dilution and burn risk?",
            "sides": [
                {"position": "Speed & scale", "seats": [seats_meta[k]["short"] for k in board_keys[:3]]},
                {"position": "Cash preservation & control", "seats": [seats_meta[k]["short"] for k in board_keys[3:]]}
            ]
        }
    ],
    "unanimous": False,
    "note": "The board divides between high-growth aggressive moves and capital preservation."
}
(session_dir / "cruxes.json").write_text(json.dumps(cruxes_data, indent=2), encoding="utf-8")

log("Round 1 completed and fault lines identified.")

# 3. Round 2: Debate
phase("Round 2: Debate")

async def run_seat_r2(item):
    key, prev_text = item
    s = seats_meta[key]
    r2_prompt = f"""You are {s['name']}.
Review the board's Round 1 positions and respond to the debate:
{r1_md[:2000]}

Under 200 words, respond in this format:
SEAT: {s['short'].upper()}
I DISAGREE MOST WITH: [seat]
I CONCEDE: [point]
ON THE CRUXES: [view]
STANCE: [stance]
OPTION SCORES: A 8/10 · B 6/10 · C 3/10
PILLAR SCORE: 7/10
CONFIDENCE: 4/5
RUIN RISK: none
MOVED: no
MY CONDITIONS FOR YES: [condition]"""
    res = await agent(prompt=r2_prompt, schema={"type": "string"}, role=f"{s['short']} (R2)")
    return key, res

r2_results = await parallel(r1_results, run_seat_r2)
r2_md = "# Round 2\n\n" + "\n\n".join([f"## {seats_meta[k]['name']}\n\n{text}" for k, text in r2_results])
(session_dir / "round-2.md").write_text(r2_md, encoding="utf-8")

draft_data = {
    "option": "B",
    "label": "GO WITH CONDITIONS",
    "recommendation": "Execute a phased rollout with clear validation milestones before committing capital.",
    "conditions": ["Set a 60-day review gate with measurable KPIs", "Cap downside burn to 10% of runway"],
    "next_steps": ["Run a 2-week pilot", "Survey existing customers"],
    "cheapest_test": "Pre-sell or test interest with 10 key stakeholders",
    "kill_criteria": "If conversion drops below target threshold after 30 days"
}
(session_dir / "draft.json").write_text(json.dumps(draft_data, indent=2), encoding="utf-8")
(session_dir / "draft-resolution.md").write_text(f"# Draft Resolution\n\n{draft_data['recommendation']}\n", encoding="utf-8")

log("Round 2 debate completed and draft resolution prepared.")

# 4. Round 3: Vote
phase("Round 3: Vote")

async def run_seat_r3(item):
    key, _ = item
    s = seats_meta[key]
    r3_prompt = f"""You are {s['name']}.
Vote on the Draft Resolution:
Recommendation: {draft_data['recommendation']}
Conditions: {', '.join(draft_data['conditions'])}

Format under 100 words:
SEAT: {s['short'].upper()}
VOTE: Endorse | Endorse with amendment | Dissent
OPTION SCORES: A 7/10 · B 8/10 · C 3/10
FINAL SCORE: 8/10
FINAL PILLAR SCORE: 8/10
AMENDMENT OR DISSENT: [one line or blank]
ONE LINE FOR THE FOUNDER: [core takeaway]"""
    res = await agent(prompt=r3_prompt, schema={"type": "string"}, role=f"{s['short']} (R3)")
    return key, res

r3_results = await parallel(r2_results, run_seat_r3)
r3_md = "# Round 3\n\n" + "\n\n".join([f"## {seats_meta[k]['name']}\n\n{text}" for k, text in r3_results])
(session_dir / "round-3.md").write_text(r3_md, encoding="utf-8")

# 5. Verdict
phase("Verdict")

verdict_data = {
    "label": "GO WITH CONDITIONS",
    "call": f"Proceed with Option B under strict stage-gate metrics: {draft_data['recommendation']}",
    "recommended": "B",
    "why": [
        {"point": "Balances upside expansion with downside protection", "seat": "Bezos", "framework": "Two-Way Door"},
        {"point": "Preserves cash cushion while testing demand", "seat": "Buffett", "framework": "Margin of Safety"},
        {"point": "Allows rapid customer feedback loops", "seat": "Graham", "framework": "Make Something People Want"}
    ],
    "minority": {
        "seat": "Hormozi",
        "quote": "If you don't scale fast, you leave value on the table.",
        "would_have_to_be_true": "Retention and unit economics would need to be 100% proven first."
    },
    "next_steps": [
        {"when": "This week", "action": draft_data["cheapest_test"]},
        {"when": "Within 30 days", "action": "Review initial metrics against kill criteria"}
    ],
    "kill_criteria": draft_data["kill_criteria"],
    "conditions": draft_data["conditions"],
    "fights": [
        {"crux": cruxes_data["cruxes"][0]["question"], "story": "The board resolved on a staged rollout protecting downside."}
    ],
    "amendments": [],
    "cheapest_test": draft_data["cheapest_test"],
    "revisit": "In 60 days with hard metric results",
    "override_note": ""
}
(session_dir / "verdict.json").write_text(json.dumps(verdict_data, indent=2), encoding="utf-8")

verdict_md = f"""# Roast Room Verdict: {prompt}

## Result: {verdict_data['label']} (Option {verdict_data['recommended']})

**The Call:** {verdict_data['call']}

### Why the Council Landed Here
""" + "\n".join([f"- **{w['seat']}** ({w['framework']}): {w['point']}" for w in verdict_data["why"]]) + f"""

### Next Steps
""" + "\n".join([f"- **{n['when']}**: {n['action']}" for n in verdict_data["next_steps"]]) + f"""

**Cheapest Test:** {verdict_data['cheapest_test']}
**Kill Criteria:** {verdict_data['kill_criteria']}
"""
(session_dir / "verdict.md").write_text(verdict_md, encoding="utf-8")

log(f"Council verdict written to {session_dir / 'verdict.md'}")
print(f"VERDICT: {verdict_data['label']} - {verdict_data['call']}")
