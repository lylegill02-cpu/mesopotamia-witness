# Mesopotamia Witness

**Mesopotamian cuneiform sources with English witness notes** — what tablets and scholarship support vs what Anunnaki / ancient-alien media claims.

Mirrors the [Bavli Uncensored](https://github.com/lylegill02-cpu/bavli-uncensored) pattern: **loci map + corpus search + witness deltas + GitHub Pages**.

## Live site

https://lylegill02-cpu.github.io/mesopotamia-witness/

- **Search** — ~394 ETCSL Sumerian texts + Akkadian trio (Enuma Elish, Atrahasis, Gilgamesh XI)
- **Flood comparison** — side-by-side motifs across Atrahasis, Gilgamesh XI, and Sumerian parallels
- **Loci map** — 12 guided passages with pop-vs-scholarly witness notes
- **Catalog** — browse ETCSL IDs and Akkadian texts

## Build from source

```bash
python scripts/build_all.py          # fetch ETCSL zip, build index, merge Akkadian, export JSON
python scripts/publish_release.py v1.1.0-search   # upload corpus.db.gz for client search
cp data/loci_chart.json web/data/
cp data/english_glossary.json web/data/
cp data/flood_comparison.json web/data/
cp data/akkadian_catalog.json web/data/
```

## Data sources

| Source | Use |
|--------|-----|
| [ETCSL](https://etcsl.orinst.ox.ac.uk/) (Oxford OTA zip, CC BY 3.0 UK) | Sumerian literary corpus + English translations |
| King 1902 / Foster-style PD composites | Enuma Elish, Atrahasis, Gilgamesh XI (English search layer) |
| [ORACC](https://oracc.museum.upenn.edu/) | AMGG lexicon links; future royal inscriptions |
| [CDLI](https://cdli.earth/) | Tablet photos & catalog links |

## Architecture

| Piece | Location |
|-------|----------|
| ETCSL zip | `data/etcsl.zip` (gitignored, fetched by script) |
| Search index | `data/corpus.db` → Release `corpus.db.gz` |
| Akkadian JSON | `data/akkadian/*.json` |
| Flood comparison | `data/flood_comparison.json` |
| Loci | `data/loci.json` + `data/witness_deltas.json` |
| Static UI | `web/` |

## License

Code: MIT. ETCSL text: [CC BY 3.0 UK](https://etcsl.orinst.ox.ac.uk/) — cite Black et al., ETCSL, Oxford 1998–2006. Akkadian PD translations: see each text’s `translation_source` in `data/akkadian/`.
