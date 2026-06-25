# Mesopotamia Witness

**Mesopotamian cuneiform sources with English witness notes** — what tablets and scholarship support vs what Anunnaki / ancient-alien media claims.

Mirrors the [Bavli Uncensored](https://github.com/lylegill02-cpu/bavli-uncensored) pattern: **loci map + ETCSL search + witness deltas + GitHub Pages**.

## Live site

https://lylegill02-cpu.github.io/mesopotamia-witness/

- **Search** — ~394 ETCSL texts (English + transliteration), ~4 MB index download once
- **Loci map** — 12 guided passages with pop-vs-scholarly witness notes
- **Catalog** — browse all ETCSL composition IDs

## Build from source

```bash
python scripts/build_all.py          # fetch ETCSL zip, build index, export JSON
python scripts/publish_release.py v1.0.0-search   # upload etcsl.db.gz for client search
cp data/loci_chart.json web/data/
cp data/english_glossary.json web/data/
```

## Data sources

| Source | Use |
|--------|-----|
| [ETCSL](https://etcsl.orinst.ox.ac.uk/) (Oxford OTA zip, CC BY 3.0 UK) | Sumerian literary corpus + English translations |
| [ORACC](https://oracc.museum.upenn.edu/) | Future: royal inscriptions (ETCSRI), AMGG |
| [CDLI](https://cdli.earth/) | Tablet photos & catalog links |

Enuma Elish, Atrahasis (Akkadian), and Anunnaki lexicon rows use **starter excerpts** until ORACC/Akkadian layers are wired.

## Architecture

| Piece | Location |
|-------|----------|
| ETCSL zip | `data/etcsl.zip` (gitignored, fetched by script) |
| Search index | `data/etcsl.db` → Release `etcsl.db.gz` |
| Loci | `data/loci.json` + `data/witness_deltas.json` |
| Static UI | `web/` |

## License

Code: MIT. ETCSL text: [CC BY 3.0 UK](https://etcsl.orinst.ox.ac.uk/) — cite Black et al., ETCSL, Oxford 1998–2006.
