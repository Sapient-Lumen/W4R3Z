# Rev277: expose boot-stdlib dependency metadata next to source inventory

Rev276 made the boot-stdlib source inventory machine-readable, but future humans,
future LLMs, and future Python/Rust/WASM hosts still had to read normalized
`definition` strings by eye to answer questions like:

- is `finally` just an alias for `ensure`?
- which tiny stdlib words does `bi` reuse?
- which referenced words are still kernel/non-stdlib dependencies?

This rev keeps the next step tiny: tokenize the existing `core.mx` definition
text, classify the referenced words, and let `mxportable` show that dependency
shape on demand.

## What changed

- `boot_stdlib_word_specs()` in `src/micromax/portability_suite.py` now also
  records, for each `: word ... ;` definition:
  - `body_tokens`
  - `syntax_tokens`
  - `literal_tokens`
  - `word_refs`
  - `stdlib_refs`
  - `nonstdlib_refs`
  - `alias_of` when the definition is just another word name
- `selected_boot_stdlib_word_inventory(...)` now carries that same dependency
  metadata in its machine-readable rows
- `tools/mxportable.py --stdlib-manifest` now accepts `--show-deps`
  - human mode prints alias/dependency rows
  - JSON mode keeps the same `source_inventory` payload, now with dependency
    metadata included per word

## Example commands

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word bi --show-deps
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word finally --show-source --show-deps --json
```

## Why this matters

The portability manifest already says which cases cover each tiny stdlib word,
and rev276 already said where those words live in `core.mx`. This rev makes the
*shape* of each definition inspectable too, without pretending Micromax needs a
richer parser or dependency graph.

That is useful during bring-up work because one tiny tool can now answer all of
these together:

1. which boot-stdlib words are supposed to be covered,
2. where each word lives and what stack effect it claims,
3. whether a word is just an alias, and
4. which words in the definition come from boot stdlib versus the smaller kernel.
