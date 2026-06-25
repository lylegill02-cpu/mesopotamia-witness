import { loadIndex } from "./client-db.js";
import { searchAll, getText } from "./client-search.js";
import { lociChartUrl, glossaryUrl } from "./config.js";
import { renderWitnessDelta, locusForTextId, locusForRef } from "./witness-delta.js";

let glossary = null;

export async function ensureSearch(onProgress) {
  await loadIndex(onProgress);
}

export async function loadGlossary() {
  if (glossary) return glossary;
  const r = await fetch(glossaryUrl());
  if (!r.ok) return { terms: [] };
  glossary = await r.json();
  return glossary;
}

export function glossaryHints(query, terms, limit = 6) {
  const q = String(query || "").toLowerCase().trim();
  if (!q) return [];
  const hits = [];
  for (const term of terms || []) {
    const bag = [term.english, ...(term.aliases || [])].join(" ").toLowerCase();
    if (bag.includes(q) || (term.aliases || []).some((a) => a.includes(q))) {
      hits.push(term);
    }
  }
  return hits.slice(0, limit);
}

export async function search(query, opts = {}) {
  return searchAll(query, opts);
}

export async function openText(textId, onProgress) {
  await ensureSearch(onProgress);
  return getText(textId);
}

export async function findLocus(textId, ref) {
  const r = await fetch(lociChartUrl());
  if (!r.ok) return null;
  const data = await r.json();
  const loci = data.loci || [];
  if (textId) {
    const byText = loci.find((x) => x.text_id === textId);
    if (byText) return byText;
  }
  if (ref) return locusForRef(loci, ref);
  return null;
}

export { renderWitnessDelta, locusForTextId, locusForRef };
