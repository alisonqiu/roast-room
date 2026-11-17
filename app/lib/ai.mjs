import { env } from "./env.mjs";
import * as anthropic from "./anthropic.mjs";
import * as gemini from "./gemini.mjs";

export function getProvider() {
  const p = (process.env.AI_PROVIDER || env("AI_PROVIDER") || "").toLowerCase();
  if (p === "gemini") return "gemini";
  if (p === "anthropic") return "anthropic";
  if (process.env.GEMINI_API_KEY || env("GEMINI_API_KEY")) return "gemini";
  if (process.env.ANTHROPIC_API_KEY || env("ANTHROPIC_API_KEY")) return "anthropic";
  return "none";
}

export function hasKey() {
  return Boolean(
    process.env.GEMINI_API_KEY ||
    env("GEMINI_API_KEY") ||
    process.env.ANTHROPIC_API_KEY ||
    env("ANTHROPIC_API_KEY")
  );
}

export function getDefaultModels() {
  const prov = getProvider();
  if (prov === "gemini") {
    return {
      seat: process.env.GEMINI_SEAT_MODEL || env("GEMINI_SEAT_MODEL") || "gemini-2.5-flash",
      chair: process.env.GEMINI_CHAIR_MODEL || env("GEMINI_CHAIR_MODEL") || "gemini-2.5-pro",
    };
  }
  return {
    seat: process.env.SEAT_MODEL || env("SEAT_MODEL") || "claude-sonnet-5-5",
    chair: process.env.CHAIR_MODEL || env("CHAIR_MODEL") || "claude-opus-5-5",
  };
}

export const usage = {
  get input() { return (getProvider() === "gemini" ? gemini.usage : anthropic.usage).input; },
  get output() { return (getProvider() === "gemini" ? gemini.usage : anthropic.usage).output; },
  get calls() { return (getProvider() === "gemini" ? gemini.usage : anthropic.usage).calls; },
};

export async function stream(args) {
  const prov = getProvider();
  if (prov === "gemini") {
    const defaultModel = process.env.GEMINI_SEAT_MODEL || env("GEMINI_SEAT_MODEL") || "gemini-2.5-flash";
    const mod = (args.model && args.model.startsWith("gemini")) ? args.model : defaultModel;
    return gemini.stream({ ...args, model: mod });
  }
  return anthropic.stream(args);
}

export async function json(args) {
  const prov = getProvider();
  if (prov === "gemini") {
    const defaultModel = process.env.GEMINI_CHAIR_MODEL || env("GEMINI_CHAIR_MODEL") || "gemini-2.5-pro";
    const mod = (args.model && args.model.startsWith("gemini")) ? args.model : defaultModel;
    return gemini.json({ ...args, model: mod });
  }
  return anthropic.json(args);
}

export { S } from "./anthropic.mjs";
