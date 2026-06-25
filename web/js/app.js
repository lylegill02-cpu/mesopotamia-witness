import { loadIndex } from "./client-db.js";
import { searchAll, getText } from "./client-search.js";
import { lociChartUrl, glossaryUrl } from "./config.js";
import { renderWitnessDelta, locusForTextId, locusForRef } from "./witness-delta.js";

let glossary = null;
let lociCache = null;

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

async function loadLoci() {
  if (lociCache) return lociCache;
  const r = await fetch(lociChartUrl());
  if (!r.ok) return [];
  lociCache = (await r.json()).loci || [];
  return lociCache;
}

function keywordMatch(loci, textId, query) {
  const q = String(query || "").toLowerCase().trim();
  if (!q || q.length < 3) return null;
  for (const loc of loci) {
    if (textId && loc.text_id === textId) return loc;
    const bag = [
      loc.needle,
      loc.ref,
      loc.topic?.en,
      ...(loc.english_keywords || []),
      ...(loc.tags || []),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    if (bag.includes(q)) return loc;
  }
  return null;
}

export async function findLocus(textId, ref, query) {
  const loci = await loadLoci();
  if (textId) {
    const byText = loci.find((x) => x.text_id === textId);
    if (byText) return byText;
  }
  if (ref) {
    const byRef = locusForRef(loci, ref);
    if (byRef) return byRef;
  }
  return keywordMatch(loci, textId, query);
}

export { renderWitnessDelta, locusForTextId, locusForRef };
