// Build-time reader for public/data/. Vite won't import JSON from public/, so read it with fs.
import fs from "node:fs";
import path from "node:path";

const DIR = path.join(process.cwd(), "public", "data");
export const read = (f: string): any => JSON.parse(fs.readFileSync(path.join(DIR, f), "utf8"));

export type Figure = { value: unknown; display: string; label: string; src: string; note: string };
export const figures: Record<string, Figure> = read("figures.json");

export function fig(id: string): Figure {
  const f = figures[id];
  if (!f) throw new Error(`figures.json has no "${id}"`);
  return f;
}

export const tagKind = (l: string) =>
  /UNVERIFIED/.test(l) ? "unv" : /OBSERVED/.test(l) ? "obs" : /ESTIMATED/.test(l) ? "est" : /SIMULATED/.test(l) ? "sim" : "asm";

// The deck tags only model output (SIMULATED); sourced figures carry a source line on the slide instead.
export const showTag = (l: string) => /^SIMULATED/.test(l);

// Short tag text; the full label goes in the title attribute.
export const tagText = (l: string) => (/^OBSERVED \(REPORT\)/.test(l) ? "observed (report)" : l.split(/[ ;/(]/)[0].toLowerCase());
