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

// Numbered references (cordon.export.references): register IDs, dataset IDs and software → one entry each.
export type Ref = { n: number; ids: string[]; author: string; title: string; published: string; url: string; where: string; status: string };
export const references: { repo: string; groups: { id: string; name: string; items: Ref[] }[]; by_id: Record<string, number> } = read("references.json");
const refByN = new Map(references.groups.flatMap((g) => g.items).map((r) => [r.n, r]));

export function ref(id: string): Ref {
  const n = references.by_id[id.trim()];
  if (!n) throw new Error(`references.json has no "${id}"`);
  return refByN.get(n)!;
}

export const repoFile = (p: string) => `${references.repo}/blob/main/${p}`;

// Hover text for a figure: the numbered sources behind it, or our model's output file.
export function figSource(id: string): string {
  const src = fig(id).src;
  const ids = src.match(/[A-Z]+(?:-[A-Z]+)?-\d{3}/g);
  if (ids) return "Source: " + [...new Set(ids.map((i) => ref(i)))].map((r) => `[${r.n}] ${r.author}, ${r.title}`).join("; ");
  if (/metrics\.json|finance\.json/.test(src)) return `Our model (${src}); method in docs/methodology.md`;
  if (/crossings|counts\.geojson/.test(src)) return `City of Toronto Open Data traffic counts [${ref("tor_tmc").n}, ${ref("tor_svc").n}], matched by us (${src})`;
  if (/nyc_transit/.test(src)) return `[${ref("N-001").n}] MTA Daily Ridership and Traffic (data.ny.gov sayj-mze2)`;
  return `From ${src}`;
}
