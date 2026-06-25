# Mesopotamia Witness

**Mesopotamian cuneiform sources with English witness notes** — what tablets and scholarship support vs what Anunnaki / ancient-alien media claims.

Mirrors the [Bavli Uncensored](https://github.com/lylegill02-cpu/bavli-uncensored) pattern: **loci map + unified search + witness deltas + GitHub Pages**.

## Live site

https://lylegill02-cpu.github.io/mesopotamia-witness/

- **Search** — ETCSL Sumerian (~394) + Akkadian trio + ORACC (AMGG Anunna, ETCSRI sample)
- **Flood comparison** — Atrahasis, Gilgamesh XI, Sumerian parallels side-by-side
- **Eridu Genesis** — fragment witness page for ETCSL `c.1.7.4`
- **Loci map** — 12 guided passages with pop-vs-scholarly witness notes

## Build from source

```bash
python scripts/build_all.py
python scripts/publish_release.py v1.2.0-search
```

`build_all.py` fetches ETCSL + ORACC HTML, merges Akkadian/ORACC JSON into `corpus.db`, validates, exports `web/data/`, and syncs loci. CI deploys committed `web/` + runs loci sync only — **publish a new Release** after rebuilding locally when search index changes.

## Data sources

| Source | Use |
|--------|-----|
| [ETCSL](https://etcsl.orinst.ox.ac.uk/) (Oxford OTA zip, CC BY 3.0 UK) | Sumerian literary corpus |
| King / Thompson PD composites | Enuma Elish, Atrahasis, Gilgamesh XI (English + sample Akkadian lines) |
| [ORACC AMGG](https://oracc.museum.upenn.edu/amgg/) (CC BY-SA 3.0) | Anunna lexicon entry |
| [ORACC ETCSRI](https://oracc.museum.upenn.edu/etcsri/) | Royal inscription sample |
| [CDLI](https://cdli.earth/) | Tablet photos & catalog links |

## Architecture

| Piece | Location |
|-------|----------|
| ETCSL zip | `data/etcsl.zip` (gitignored) |
| Extra corpus JSON | `data/akkadian/`, `data/oracc/` |
| Search index | `data/corpus.db` → Release `corpus.db.gz` |
| Loci | `data/loci.json` + `data/witness_deltas.json` |
| Static UI | `web/` |

## License

Code: MIT. ETCSL: [CC BY 3.0 UK](https://etcsl.orinst.ox.ac.uk/). ORACC AMGG/ETCSRI: [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).
