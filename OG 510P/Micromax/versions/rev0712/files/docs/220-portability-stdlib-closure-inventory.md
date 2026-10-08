# Rev278: expose boot-stdlib prerequisite closure next to direct dependency inventory

Rev277 made the direct dependency shape of each `core.mx` word machine-readable,
but future humans, future LLMs, and future Python/Rust/WASM hosts still had to
recurse through those rows by hand to answer bring-up questions like:

- what kernel-sized words does `finally` *really* need?
- is `recover` just an alias for `try`, and if so what does that imply for a
  minimal port?
- in what small stdlib order should I bring up `bi` or `tri`?

This rev keeps the next step tiny: derive one transitive prerequisite closure
from the same parsed `core.mx` definitions and let `mxportable` show it on
demand.

## What changed

- `boot_stdlib_word_specs()` in `src/micromax/portability_suite.py` now also
  records, for each `: word ... ;` definition:
  - `dependency_order`
  - `transitive_stdlib_refs`
  - `transitive_nonstdlib_refs`
  - `stdlib_depth`
- `selected_boot_stdlib_word_inventory(...)` now carries that same closure
  metadata in its machine-readable rows
- `tools/mxportable.py --stdlib-manifest` now accepts `--show-closure`
  - human mode prints dependency order, transitive stdlib refs, transitive
    nonstdlib refs, and stdlib depth
  - JSON mode keeps the same `source_inventory` payload, now with closure
    metadata included per word

## Example commands

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word finally --show-closure
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word bi --show-source --show-closure --json
```

## Why this matters

The portability manifest already says which cases cover each tiny stdlib word.
Rev276 already said where those words live in `core.mx`, and rev277 said what
each definition directly mentions.

Rev278 answers the next practical bring-up question without pretending Micromax
needs a richer parser or whole-program graph: if a word is an alias or a small
composition of other words, what prerequisites actually sit underneath it?

That is useful during bring-up work because one tiny tool can now answer all of
these together:

1. which boot-stdlib words are supposed to be covered,
2. where each word lives and what stack effect it claims,
3. what each word directly references, and
4. which stdlib and kernel-sized prerequisites must already exist for a minimal
   implementation of that word.
