# Rev275: make the boot-stdlib portability manifest inspectable outside pytest

Rev259 made boot-stdlib portability coverage explicit, but the manifest still
lived only inside `tests/test_portability_suite.py`. That was good enough for
pytest, but awkward for future humans, future LLMs, and future Python/Rust/WASM
hosts that want to answer simple questions like:

- which boot-stdlib words have explicit portability cases?
- which case names belong to `try`, `ensure`, or `rdrop`?
- does the currently selected portability corpus actually cover every mapped
  boot-stdlib word?

This rev moves that manifest into shared source and teaches `mxportable` to show
it directly.

## What changed

- `src/micromax/portability_suite.py` now exports:
  - `BOOT_STDLIB_PORTABILITY_MANIFEST`
  - `boot_stdlib_portability_manifest()`
  - `select_boot_stdlib_manifest_entries(...)`
  - `boot_stdlib_manifest_inventory(...)`
- `tools/mxportable.py` now supports:
  - `--stdlib-manifest`
  - repeatable `--word WORD`
  - `--word-contains SUBSTRING`
  - `--json` for the manifest view too
- `tests/test_portability_suite.py` now reuses the shared manifest instead of
  keeping a second copy of the mapping inside the test file.

## Example commands

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word try --word ensure
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word-contains try --json
```

## Why this matters

The portability corpus is already one of the best cross-host contracts in the
repo. This rev makes the *coverage map* inspectable too, without requiring
pytest imports or manual scraping of test source. That is especially helpful
for future LLMs and hand ports, because they can now ask one tool for both:

1. the replayable behavior cases, and
2. the tiny manifest that says which boot-stdlib words those cases are meant to
   cover.
