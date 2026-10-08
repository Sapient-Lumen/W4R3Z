# Rev276: expose boot-stdlib source metadata alongside the portability manifest

Rev275 made the boot-stdlib portability manifest inspectable outside pytest, but
future humans, future LLMs, and future Python/Rust/WASM hosts still had to grep
`src/micromax/stdlib/core.mx` to answer simple follow-up questions like:

- where is `try` defined?
- what stack-effect comment does `ensure` claim?
- what is the current one-line/normalized definition body for `finally`?

This rev keeps the next step tiny: parse the existing boot stdlib source once,
keep the result machine-friendly, and let `mxportable` show it on demand.

## What changed

- `src/micromax/portability_suite.py` now exports:
  - `boot_stdlib_source_path()`
  - `boot_stdlib_word_specs()`
  - `selected_boot_stdlib_word_inventory(...)`
- `boot_stdlib_word_specs()` scans `src/micromax/stdlib/core.mx` and records, for
  each `: word ... ;` definition:
  - the word name
  - the starting source line
  - the stack-effect comment, if present
  - a normalized definition body string
  - the source path
- `tools/mxportable.py --stdlib-manifest` now accepts `--show-source`
  - human mode prints `core.mx:<line>` plus stack effect and definition text
  - JSON mode adds a sibling `source_inventory` payload

## Example commands

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word try --show-source
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-source --json
```

## Why this matters

The portability corpus already says which cases cover each tiny stdlib word. This
rev makes the *source side* just as inspectable, without forcing future hosts or
future LLMs to scrape `core.mx` by hand.

That is especially helpful during bring-up work, because one tool can now answer
all three of these questions together:

1. which boot-stdlib words are meant to be covered,
2. which portability case names provide that coverage, and
3. where the covered word lives in `core.mx`, including its stack comment and
   current definition text.
