# Mesopotamia Witness

**Mesopotamian cuneiform sources with English witness notes** — what tablets and scholarship support vs what Anunnaki / ancient-alien media claims.

Mirrors the [Bavli Uncensored](https://github.com/lylegill02-cpu/bavli-uncensored) pattern: **loci map + witness deltas + static GitHub Pages**. The problem here is not Vilna censorship but **interpretation drift** (Sitchin-era mistranslations, gap-free paraphrases, viral summaries).

## Live site

*(Enable GitHub Pages after first push — URL will be `https://lylegill02-cpu.github.io/mesopotamia-witness/`)*

## Quick start

```bash
python scripts/merge_witness_deltas.py
python scripts/sync_loci.py
cp data/loci_chart.json web/data/loci_chart.json
cp data/corpus.json web/data/corpus.json
# open web/index.html locally, or:
python -m http.server 8080 --directory web
```

## Architecture

| Piece | Location |
|-------|----------|
| Loci seed | `data/loci.json` + `data/witness_deltas.json` |
| Starter corpus | `data/corpus.json` (9 excerpt refs — expand via ORACC) |
| Static UI | `web/` — `index.html`, `loci.html`, `text.html` |

## Starter loci (12)

- **Anunnaki** — divine council, not astronauts  
- **Enuma Elish / Tiamat** — myth vs “planet collision”  
- **Atrahasis** — human creation & flood  
- **Gilgamesh XI** — Utnapishtim  
- **Sumerian King List** — antediluvian reigns as literary time  
- **Debunk rows** — Nibiru planet, gold-mining slaves  
- **Method row** — clay witnesses & lacunae  

## Data sources (target)

- [ORACC](https://oracc.museum.upenn.edu/) — ETCSL, AMGG (CC0 JSON)
- [CDLI](https://cdli.ucla.edu/) — tablet photos & catalog
- Academic translations (George, Foster, Lambert, etc.)

`scripts/build_corpus.py` will pull ORACC when endpoints are stable; v0 ships curated starter excerpts.

## License

Corpus text: follow source licenses (ORACC CC0 for fetched data). Project code & witness notes: MIT.
