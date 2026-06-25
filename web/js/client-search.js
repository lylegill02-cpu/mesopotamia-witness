import { getDb } from "./client-db.js";

function escLike(q) {
  return String(q || "").replace(/\\/g, "\\\\").replace(/%/g, "\\%").replace(/_/g, "\\_");
}

function norm(q) {
  return String(q || "").toLowerCase().trim();
}

function snippet(text, query, width = 180) {
  const q = norm(query);
  const lower = String(text || "").toLowerCase();
  let pos = lower.indexOf(q);
  if (pos === -1) return String(text || "").slice(0, width);
  const start = Math.max(0, pos - Math.floor(width / 3));
  const end = Math.min(text.length, pos + query.length + Math.floor(width / 2));
  let out = text.slice(start, end);
  if (start > 0) out = "…" + out;
  if (end < text.length) out = out + "…";
  return out;
}

export function searchEnglish(query, { limit = 25 } = {}) {
  const conn = getDb();
  const q = escLike(norm(query));
  const stmt = conn.prepare(`
    SELECT p.text_id, COALESCE(t.corpus, 'etcsl') AS corpus, t.title, p.line_range, p.translation AS text
    FROM paragraphs p
    JOIN texts t ON t.text_id = p.text_id
    WHERE p.translation_norm LIKE '%' || ? ESCAPE '\\'
    ORDER BY t.text_id, COALESCE(p.ord, p.line_start, 9999), p.id
    LIMIT ?
  `);
  stmt.bind([q, limit]);
  const hits = [];
  while (stmt.step()) {
    const row = stmt.getAsObject();
    hits.push({
      ...row,
      layer: "translation",
      snippet: snippet(row.text, query),
    });
  }
  stmt.free();
  return hits;
}

export function searchTransliteration(query, { limit = 25 } = {}) {
  const conn = getDb();
  const q = escLike(norm(query));
  const stmt = conn.prepare(`
    SELECT l.text_id, COALESCE(t.corpus, 'etcsl') AS corpus, t.title, l.line_label, l.transliteration AS text
    FROM lines l
    JOIN texts t ON t.text_id = l.text_id
    WHERE l.translit_norm LIKE '%' || ? ESCAPE '\\'
    ORDER BY l.text_id, l.ord
    LIMIT ?
  `);
  stmt.bind([q, limit]);
  const hits = [];
  while (stmt.step()) {
    const row = stmt.getAsObject();
    hits.push({
      ...row,
      layer: "transliteration",
      snippet: snippet(row.text, query),
    });
  }
  stmt.free();
  return hits;
}

export function searchAll(query, { limit = 30 } = {}) {
  const half = Math.ceil(limit / 2);
  const en = searchEnglish(query, { limit: half });
  const su = searchTransliteration(query, { limit: half });
  return [...en, ...su].slice(0, limit);
}

export function getText(textId) {
  const conn = getDb();
  const meta = conn.prepare(
    "SELECT text_id, title, COALESCE(corpus,'etcsl') AS corpus FROM texts WHERE text_id = ?"
  );
  meta.bind([textId]);
  if (!meta.step()) {
    meta.free();
    return null;
  }
  const { text_id, title, corpus } = meta.getAsObject();
  meta.free();

  const linesStmt = conn.prepare(`
    SELECT line_label, transliteration FROM lines
    WHERE text_id = ? ORDER BY ord
  `);
  linesStmt.bind([textId]);
  const lines = [];
  while (linesStmt.step()) {
    lines.push(linesStmt.getAsObject());
  }
  linesStmt.free();

  const paraStmt = conn.prepare(`
    SELECT line_range, translation FROM paragraphs
    WHERE text_id = ? ORDER BY COALESCE(ord, line_start, 9999), id
  `);
  paraStmt.bind([textId]);
  const paragraphs = [];
  while (paraStmt.step()) {
    paragraphs.push(paraStmt.getAsObject());
  }
  paraStmt.free();

  if (!lines.length && !paragraphs.length) return null;
  return { text_id, title, corpus, lines, paragraphs };
}

export function listTexts({ q = "", limit = 50 } = {}) {
  const conn = getDb();
  if (!q.trim()) {
    const res = conn.exec(`SELECT text_id, title FROM texts ORDER BY text_id LIMIT ${limit}`);
    if (!res.length) return [];
    return res[0].values.map(([text_id, title]) => ({ text_id, title }));
  }
  const stmt = conn.prepare(`
    SELECT text_id, title FROM texts
    WHERE lower(title) LIKE '%' || ? ESCAPE '\\'
    ORDER BY text_id LIMIT ?
  `);
  stmt.bind([escLike(norm(q)), limit]);
  const out = [];
  while (stmt.step()) out.push(stmt.getAsObject());
  stmt.free();
  return out;
}
