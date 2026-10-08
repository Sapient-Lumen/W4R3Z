# Rev279 — boot-stdlib reverse user inventory

## What changed

`mxportable --stdlib-manifest` now supports `--show-users`, exposing a tiny reverse usage view for each boot stdlib word alongside the existing manifest, source, dependency, and closure metadata.

The shared source helper `boot_stdlib_word_specs()` now derives three extra fields from `src/micromax/stdlib/core.mx`:

- `direct_stdlib_users` — boot stdlib words that directly reference this word
- `transitive_stdlib_users` — boot stdlib words that depend on this word anywhere in their stdlib prerequisite chain
- `user_depth` — maximum reverse dependency depth among boot stdlib users

`selected_boot_stdlib_word_inventory(...)` now includes the same fields, and `tools/mxportable.py` can render them in both human and JSON modes.

## Why this matters

Rev275–rev278 made it easy to answer:

- which portability cases cover a word
- where the word lives in `core.mx`
- which words it directly references
- which transitive prerequisites it needs to boot

The missing inverse question was: **who depends on this word?**

That matters for:

- tiny host bring-up planning
- deciding what to retest after changing a small combinator
- helping future LLMs avoid re-reading `core.mx` recursively to infer impact

## Example

Human view:

```text
python tools/mxportable.py --stdlib-manifest --word keep --show-users
```

JSON view:

```text
python tools/mxportable.py --stdlib-manifest --word ensure --show-source --show-users --json
```

Example facts this now exposes directly:

- `keep` has direct/transitive users `bi`, `tri`
- `ensure` has direct/transitive user `finally`
- words with no higher-level stdlib users report `-` and depth `0`

## Design constraint

This intentionally stays tiny and source-driven. We still do **not** build a richer AST or compiler graph for `core.mx`; we only reuse the already-extracted colon-definition metadata and reverse the stdlib reference edges.
