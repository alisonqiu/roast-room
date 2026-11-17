# Roast Room · Antigravity Edition

![The Roast Room](docs/room.jpg)

Bring a hard business decision and a council of AI advisors argues it out, then hands you a scored verdict and a one-click PDF. Twelve advisors ship with it, each built from that person's public work: their letters, essays, talks, and videos. For each question, the Chair recommends who should sit on the council and you confirm. 

The council runs natively in **Google Antigravity** (with support for Claude Code), and a zero-dependency local web app shows them around an interactive table debating in real time—complete with live cartoon portrait lip-syncing, speech bubbles, conflict links, and real-time scoreboards.

Want someone else at the table? Type `/newroaster` and a name, and Antigravity builds that advisor from their public work.

| Seat | Pillar | The question they own |
|---|---|---|
| Jeff Bezos | Strategy and decisions | Is this the right bet, and how reversible is it? |
| Paul Graham | Product and startups | Do people actually want this, and is it growing? |
| Alex Hormozi | Offers, pricing, and sales | Will people pay, how much, and how do we close? |
| Gary Vaynerchuk | Marketing and attention | Where does the attention come from? |
| Dan Martell | People, hiring, and founder time | Who does this, and what does it cost your calendar? |
| Gino Wickman | Operations and scaling | Can the business run this without you holding it together? |
| Warren Buffett | Money and capital | What does it do to cash, risk, and long-term value? |

Those seven are the **default board**. Five more advisors are on call, and the Chair brings them in when your question is in their lane:

| Seat | Pillar | The question they own |
|---|---|---|
| Naval Ravikant | Leverage and wealth | Does this build leverage and equity you own, or does it just rent out your time? |
| Codie Sanchez | Buying and owning small businesses | Should you build this, or buy something that already works? |
| Leila Hormozi | Leadership and scaling teams | Can your team and your leadership carry this, and who has to change? |
| Sara Blakely | Consumer product and brand from zero | Will customers love it enough to sell it for you, without outside money? |
| Elon Musk | First principles and execution speed | What is the real constraint here, and can we cut steps and build it faster? |

---

## What you need

- **[Google Antigravity](https://deepmind.google)** (or Claude Code).
- **[Node.js](https://nodejs.org)** 20 or newer for the web app (zero npm dependencies to install).
- *(Optional)* A **Google Gemini API key** (`GEMINI_API_KEY`) or **Anthropic API key** (`ANTHROPIC_API_KEY`) if you want the web app or CLI to run councils directly without agent chat.

---

## Setup

```bash
git clone https://github.com/alisonqiu/roast-room.git
cd roast-room
```

Or open Antigravity anywhere and say:  
> *"Clone github.com/alisonqiu/roast-room and start the room for me."*

---

## Run a roast

### Option 1: In Antigravity (No API Key Required)
1. Start the room:
   ```bash
   npm start
   ```
2. Open **http://localhost:4730** in your browser and leave it open.
3. In Antigravity chat, tell the agent:
   > *"Roast this decision: [your question or dilemma]"*
4. Antigravity acts as the **Chair**: it seats the board, runs Round 1 (Openings), Cruxes (Fault Lines), Round 2 (Debate), Round 3 (Votes), and writes the final verdict.
5. Watch the table at **http://localhost:4730** animate each advisor speaking, rebutting, and voting live!
6. Click **Download PDF** when the verdict lands.

### Option 2: Directly in the Browser (Autonomous Web Runner)
1. Copy `.env.example` to `.env` and set `GEMINI_API_KEY` (or `ANTHROPIC_API_KEY`):
   ```bash
   cp .env.example .env
   # Add GEMINI_API_KEY=your_key
   ```
2. Run `npm start` and open **http://localhost:4730**.
3. Click **"Enter question here"** in the center of the table.
4. Type your decision, select **Full council** (7 seats, 3 rounds) or **Quick** (4 seats, 2 rounds), and click **Convene the council**.

### Option 3: Terminal CLI
Run a council directly from your terminal:
```bash
npm run roast "Should I raise a seed round or stay bootstrapped?" --quick
```

---

## What to put in your question

The council is only as good as what you give it. Include:

- **The decision** in one line.
- **Your options.** Two or three. *"Keep doing what I do now"* counts.
- **Your numbers.** Revenue, cash, margins, and team size.
- **Your limits.** Deadline, hours, and budget.
- **What success looks like**, and by when.
- **Which way you're leaning**, and why. The council tests your lean instead of echoing it.

Left something out? The Chair asks before the council starts. Example:

```
Roast this decision: I run a coaching business at $30k a month with 15 clients at $2,000 each.
Should I raise to $3,500 for everyone, raise for new clients only, or keep $2,000?
Close rate is about 50% and I have $40k in the bank. Success is $45k a month by March.
I'm leaning toward raising for everyone because I'm underpaid.
```

More ways to run it in chat:

- `Roast this decision: ... --quick` seats four advisors for two rounds. Use it for smaller, reversible calls.
- `Roast this decision: ... --seats hormozi,buffett` seats only the advisors you name.
- `Ask advisor hormozi: ...` gets one consult answer from one seat.
- `Roast this decision: ... --all` seats every advisor you have (up to nine).
- `Roast room board` shows who sits at the table by default and lets you customize it.

---

## Choose who sits at the table

When you convene the council, the Chair reads your question and recommends a council from every advisor you have, with one line on why each one fits. You pick:

- **Recommended board**: the five to seven advisors the Chair picked for this question.
- **Default board**: your usual seven.
- **Everyone**: all of them, when you have nine or fewer.
- **Other**: type changes, like *"recommended, but add Naval and drop Wickman"*.

A pricing question might get Hormozi, Buffett, Codie Sanchez, Sara Blakely, and Graham. A hiring question might get Leila Hormozi, Martell, Wickman, Naval, and Buffett. Every council keeps a seat that guards your downside and one that's likely to disagree, so the room argues instead of nodding.

How the board gets picked is configured in `.claude/skills/roast-room/roster.json`:

```json
{
  "board": "ask",
  "default": ["bezos", "graham", "hormozi", "garyvee", "martell", "wickman", "buffett"],
  "seats": [ ...every advisor you have... ]
}
```

| Setting | What happens on every council |
|---|---|
| `"ask"` (default) | The Chair recommends a council and asks you to confirm it. |
| `"auto"` | The Chair picks the council and tells you who and why, without asking. |
| `"default"` | Your default board sits every time. No question. |

---

## Add your own advisor with `/newroaster`

```
/newroaster Morgan Housel
```

Antigravity builds a new seat the way the original twelve were built:

1. **Asks two or three questions**: the business pillar and question the advisor owns, whether they join your default board, and depth.
2. **Finds their public work**: essays, letters, talks, and long interviews where they are the primary speaker.
3. **Fetches it** into `build/<name>/` (git-ignored). Web pages become text and YouTube videos become transcripts.
4. **Extracts how they think**: analyzes sources to extract frameworks, rules, positions, stories, and voice, with verbatim quotes.
5. **Writes the brain** (`.claude/skills/roast-room/brains/<name>/`) and checks that every quote is word for word in the source it cites.
6. **Registers the advisor** in `roster.json` and creates `.claude/agents/council-<name>.md`.
7. **Makes their portrait** for the room from a photo, in the same animated cartoon style.
8. **Tests the new seat** on a sample question.

---

## How it works under the hood

- **Antigravity acts as the Chair.** Guided by `GEMINI.md` and `.agents/skills/roast-room/SKILL.md`, Antigravity runs the multi-round debate protocol. Each seat reasons from its own brain (`.claude/skills/roast-room/brains/<name>/`), with frameworks, principles, positions, stories, and voice notes compiled from verified public work.
- **Scored evaluation & overrides.** Each seat scores every option, weighted by how much that seat's pillar matters to your decision. The Chair caps the verdict when a seat flags ruin risk, and forces cross-examination debate when opinions diverge.
- **File-driven live playback.** As the Chair works, it writes round files to `sessions/` in real time:
  1. `council.json` & `brief.md` (Setup)
  2. `round-1.md` & `cruxes.json` (Openings & identified fault lines)
  3. `round-2.md` & `draft.json` (Cross-examination debate & draft resolution)
  4. `round-3.md` (Ratification votes & amendments)
  5. `verdict.json` & `verdict.md` (Final verdict & scored options)
- **Universal AI Engine.** When running autonomously via the web composer or CLI, `app/lib/ai.mjs` automatically routes calls to Google Gemini (`gemini.mjs`) or Anthropic (`anthropic.mjs`), with streaming token counts and JSON schema enforcement.
- **Every council is saved.** Saved sessions are kept in `sessions/` and can be replayed at any time or downloaded as a branded PDF from the web interface.

---

## What's inside

| Path | What |
|---|---|
| `GEMINI.md` | Antigravity project rules and Chair execution instructions |
| `.agents/skills/` | Antigravity workspace skills for `roast-room` and `newroaster` |
| `.claude/skills/roast-room/` | The council protocol, prompts, scoring math, and advisor brains |
| `.claude/skills/roast-room/roster.json` | Advisors metadata, pillars, default board, and board selection mode |
| `app/` | Zero-dependency Node server, public web client, and PDF exporter |
| `app/lib/gemini.mjs` | Native Google Gemini REST integration with streaming SSE |
| `app/lib/ai.mjs` | Universal multi-provider AI engine (Gemini & Anthropic) |
| `app/scripts/roast.mjs` | CLI runner (`npm run roast`) |
| `app/scripts/roast_workflow.py` | Antigravity dynamic agent workflow script |
| `sessions/` | Saved councils (kept out of git) and example sessions |

---

## About the advisors

These are simulations built from each person's public work, and so is any advisor you add. They are not the people, they don't speak for them, and none of them is affiliated with or endorses this project. A seat only quotes a person verbatim when the line is in its brain with a source.

Built by AI Automation Society. Adapted for Google Antigravity. The code is MIT licensed; see `LICENSE`.
