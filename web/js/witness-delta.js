/** English witness-delta blocks — scholarly vs popular claims. */

function trustLabel(level) {
  if (level === "high") return "English summaries: scholarly sources align well here";
  if (level === "medium") return "English summaries: compare editions carefully";
  return "English summaries: pop culture often wrong — read notes below";
}

function trustClass(level) {
  if (level === "high") return "trust-high";
  if (level === "medium") return "trust-medium";
  return "trust-low";
}

function deltaFields(d) {
  return {
    standard: d.standard_text || d.vilna_standard || d.popular_claim || "",
    witness: d.witness_reading || d.scholarly_reading || "",
    plain: d.plain_english || "",
    trust: d.trust_level || d.sefaria_trust || "medium",
    note: d.trust_note || d.sefaria_note || "",
  };
}

export function renderWitnessDelta(loc, { compact = false } = {}) {
  const d = loc?.witness_delta;
  if (!d) return "";
  const f = deltaFields(d);

  if (compact) {
    return (
      `<div class="witness-delta compact">` +
      `<p class="plain"><strong>In plain English:</strong> ${escapeHtml(f.plain)}</p>` +
      `<p class="trust ${trustClass(f.trust)}">${escapeHtml(trustLabel(f.trust))}</p>` +
      `</div>`
    );
  }

  return (
    `<div class="witness-delta">` +
    `<h4>What you can trust in English</h4>` +
    `<p class="plain"><strong>In plain English:</strong> ${escapeHtml(f.plain)}</p>` +
    `<dl>` +
    `<dt>Pop culture / viral claim</dt>` +
    `<dd>${escapeHtml(f.standard)}</dd>` +
    `<dt>Tablets & scholarship (this build)</dt>` +
    `<dd>${escapeHtml(f.witness)}</dd>` +
    `</dl>` +
    `<p class="trust ${trustClass(f.trust)}"><strong>${escapeHtml(trustLabel(f.trust))}.</strong> ${escapeHtml(f.note)}</p>` +
    `</div>`
  );
}

function escapeHtml(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export function locusForRef(loci, ref) {
  if (!ref || !loci?.length) return null;
  return loci.find((x) => x.ref === ref) || null;
}
