#!/usr/bin/env node
import { startCouncil, getSession } from "../lib/council.mjs";
import { loadRoster } from "../lib/seats.mjs";
import { hasKey, getProvider } from "../lib/ai.mjs";

loadRoster();

const args = process.argv.slice(2);
const quick = args.includes("--quick");
const promptParts = args.filter((a) => a !== "--quick");
const prompt = promptParts.join(" ").trim();

if (!prompt) {
  console.log("Usage: node app/scripts/roast.mjs \"<business decision>\" [--quick]");
  console.log("Example: node app/scripts/roast.mjs \"Should I raise seed funding or stay bootstrapped?\" --quick");
  process.exit(1);
}

if (!hasKey()) {
  console.error("Warning: Neither GEMINI_API_KEY nor ANTHROPIC_API_KEY was found in environment or .env.");
  console.error("Set GEMINI_API_KEY or ANTHROPIC_API_KEY in .env to run with AI.");
  process.exit(1);
}

console.log(`Starting Roast Room council with provider: ${getProvider()} (mode: ${quick ? "quick" : "full"})...`);
console.log(`Prompt: "${prompt}"\n`);

const session = startCouncil(prompt, quick ? "quick" : "full");

const originalEmit = session.emit || (() => {});
let lastPhase = "";

// Poll or hook into events
const checkInterval = setInterval(() => {
  const currentEvents = session.events.slice();
  for (const ev of currentEvents) {
    if (ev.type === "phase" && ev.label !== lastPhase) {
      lastPhase = ev.label;
      console.log(`\n=== [${ev.phase.toUpperCase()}] ${ev.label} ===`);
    } else if (ev.type === "seat_start") {
      process.stdout.write(`  Advisor [${ev.seat.toUpperCase()}] is speaking... `);
    } else if (ev.type === "seat_done") {
      console.log(`done (Stance: ${ev.parsed?.stance || "voted"})`);
    }
  }

  if (session.status === "done") {
    clearInterval(checkInterval);
    console.log("\n==========================================");
    console.log(`VERDICT: ${session.state?.verdict?.label || "COMPLETED"}`);
    console.log(`Recommendation: Option ${session.state?.verdict?.recommended}`);
    console.log(`Call: ${session.state?.verdict?.call}`);
    console.log(`Saved session folder: ${session.dir}`);
    console.log("==========================================\n");
    process.exit(0);
  } else if (session.status === "error") {
    clearInterval(checkInterval);
    console.error("\nCouncil ended with error.");
    process.exit(1);
  }
}, 500);
