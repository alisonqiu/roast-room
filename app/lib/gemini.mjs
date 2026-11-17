import { env } from "./env.mjs";

const BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models";
const RETRY = new Set([429, 500, 502, 503]);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function apiKey() {
  return env("GEMINI_API_KEY") || process.env.GEMINI_API_KEY || "";
}

// Running token tally for Gemini calls
export const usage = { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, calls: 0 };
function addUsage(u = {}) {
  usage.input += u.promptTokenCount || 0;
  usage.output += u.candidatesTokenCount || 0;
  usage.calls += 1;
}

// Strip properties that Gemini's strict responseSchema validator rejects
function cleanSchema(s) {
  if (!s || typeof s !== "object") return s;
  if (Array.isArray(s)) return s.map(cleanSchema);
  const out = {};
  for (const [k, v] of Object.entries(s)) {
    if (k === "additionalProperties") continue;
    out[k] = cleanSchema(v);
  }
  return out;
}

/** Stream a message using Gemini generateContent streaming (SSE). */
export async function stream({ model, system, messages, maxTokens = 2000, onText = () => {} }) {
  const key = apiKey();
  if (!key) throw new Error("GEMINI_API_KEY is not set in environment or .env");
  const mod = (model && model.startsWith("gemini")) ? model : (process.env.GEMINI_SEAT_MODEL || env("GEMINI_SEAT_MODEL") || "gemini-2.5-flash");
  const url = `${BASE_URL}/${mod}:streamGenerateContent?alt=sse&key=${key}`;

  const promptText = messages.map((m) => (typeof m.content === "string" ? m.content : JSON.stringify(m.content))).join("\n\n");
  const systemText = Array.isArray(system)
    ? system.map((s) => s.text || "").join("\n\n")
    : typeof system === "string"
    ? system
    : "";

  const body = {
    contents: [{ role: "user", parts: [{ text: promptText }] }],
    generationConfig: {
      maxOutputTokens: maxTokens,
      temperature: 0.7,
    },
  };
  if (systemText) {
    body.systemInstruction = { parts: [{ text: systemText }] };
  }

  for (let attempt = 0; attempt < 6; attempt++) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (RETRY.has(res.status)) {
      await sleep(Math.min(30000, 2000 * 2 ** attempt));
      continue;
    }
    if (!res.ok) throw new Error(`Gemini ${res.status}: ${(await res.text()).slice(0, 300)}`);

    let text = "";
    let buf = "";
    const dec = new TextDecoder();
    for await (const chunk of res.body) {
      buf += dec.decode(chunk, { stream: true });
      let i;
      while ((i = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, i).trim();
        buf = buf.slice(i + 1);
        if (!line.startsWith("data:")) continue;
        let ev;
        try { ev = JSON.parse(line.slice(5).trim()); } catch { continue; }
        const candidate = ev.candidates?.[0];
        const partText = candidate?.content?.parts?.[0]?.text;
        if (partText) {
          text += partText;
          onText(partText);
        }
        if (ev.usageMetadata) addUsage(ev.usageMetadata);
      }
    }
    return text;
  }
  throw new Error("Gemini API kept refusing after retries");
}

/** One call with structured JSON output matching schema. */
export async function json({ model, system, prompt, schema, maxTokens = 4000 }) {
  const key = apiKey();
  if (!key) throw new Error("GEMINI_API_KEY is not set in environment or .env");
  const mod = (model && model.startsWith("gemini")) ? model : (process.env.GEMINI_CHAIR_MODEL || env("GEMINI_CHAIR_MODEL") || "gemini-2.5-pro");
  const url = `${BASE_URL}/${mod}:generateContent?key=${key}`;

  const systemText = Array.isArray(system)
    ? system.map((s) => s.text || "").join("\n\n")
    : typeof system === "string"
    ? system
    : "";

  const body = {
    contents: [{ role: "user", parts: [{ text: prompt }] }],
    generationConfig: {
      maxOutputTokens: maxTokens,
      temperature: 0.2,
      responseMimeType: "application/json",
      responseSchema: cleanSchema(schema),
    },
  };
  if (systemText) {
    body.systemInstruction = { parts: [{ text: systemText }] };
  }

  for (let attempt = 0; attempt < 6; attempt++) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (RETRY.has(res.status)) {
      await sleep(Math.min(30000, 2000 * 2 ** attempt));
      continue;
    }
    if (!res.ok) throw new Error(`Gemini ${res.status}: ${(await res.text()).slice(0, 300)}`);
    const j = await res.json();
    if (j.usageMetadata) addUsage(j.usageMetadata);
    const text = j.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
    return JSON.parse(text);
  }
  throw new Error("Gemini API kept refusing after retries");
}
