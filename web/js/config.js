/** Site config — works locally and on GitHub Pages. */
export const REPO = "lylegill02-cpu/mesopotamia-witness";
export function etcsriCatalogUrl() {
  return assetUrl("/data/etcsri_catalog.json");
}

export const DB_RELEASE_TAG = "v1.3.0-search";

export function basePath() {
  const m = location.pathname.match(/^(\/[^/]+)\//);
  if (m && m[1] !== "/js" && location.hostname.endsWith("github.io")) {
    return m[1];
  }
  return "";
}

export function assetUrl(path) {
  const base = basePath();
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

export function lociChartUrl() {
  return assetUrl("/data/loci_chart.json");
}

export function corpusUrl() {
  return assetUrl("/data/corpus.json");
}

export function glossaryUrl() {
  return assetUrl("/data/english_glossary.json");
}

export function etcslTextsUrl() {
  return assetUrl("/data/etcsl_texts.json");
}

export function floodComparisonUrl() {
  return assetUrl("/data/flood_comparison.json");
}

export function akkadianCatalogUrl() {
  return assetUrl("/data/akkadian_catalog.json");
}

export function oraccCatalogUrl() {
  return assetUrl("/data/oracc_catalog.json");
}

export function dbDownloadUrl() {
  const base = `https://github.com/${REPO}/releases/download/${DB_RELEASE_TAG}`;
  return `${base}/corpus.db.gz`;
}

export function dbDownloadUrlFallback() {
  return `https://github.com/${REPO}/releases/download/v1.2.0-search/corpus.db.gz`;
}
