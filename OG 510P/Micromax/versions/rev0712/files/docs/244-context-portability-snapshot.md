# Rev302 — repo context should expose a tiny portability snapshot too

`tools/mxcontext.py` already told humans and future LLMs where to start.

That was useful, but one practical handoff question still required opening a few
extra files by hand:

- how big is the current JSON portability corpus?
- are the boot-stdlib manifest cases actually all present?
- where are the portability entrypoints in source?
- how much alias/dependency shape does the current boot stdlib have?

Rev302 keeps the context helper small, but lets it answer those questions
immediately.

```bash
python tools/mxcontext.py
python tools/mxcontext.py --json
```

## What is new

The context snapshot now also carries a compact `portability` section with:

- `kernel_cases_path`
- total portability `case_count`
- per-category counts (`kernel`, `stdlib`, ...)
- aggregated tag and host-feature counts
- a tiny boot-stdlib manifest summary
  - manifest word count
  - referenced case count
  - whether all referenced cases are present
  - any missing words
- a tiny boot-stdlib source summary
  - source path
  - definition count
  - alias count / alias words
  - maximum observed stdlib dependency depth

The curated context surfaces now also point directly at:

- `src/micromax/portability_suite.py`
- `portability/kernel_cases.json`
- a few high-value `mxportable` commands

## Why this is the right size

Micromax still does **not** want a heavyweight repo indexer.

The archive-first workflow works best when the first answer is small and stable:

- a human can skim it
- CI can validate it
- a future LLM can consume it offline
- deeper tools (`mxportable`, tests, docs) stay available for follow-up drills

So the right move is one compact summary that points at the portability truth,
not another larger inventory format.

## Focused validation

Rev302 focused validation covered:

- `tests/test_mxcontext.py`
