# Rev282: join selected boot-stdlib impact slices back to portability inventory

Rev281 made change impact executable, but there was still one tiny context gap
between “rerun these exact case names” and “what kind of contract surface am I
actually touching?”

This rev keeps the follow-up intentionally small: reuse the already-selected
impact case names, join them back to the portability corpus, and let the shared
inventory surface category/tag summaries alongside the exact replay command.

## What changed

- `src/micromax/portability_suite.py` now also provides:
  - `portability_cases_by_name(...)`
  - `impact_inventory_fields(...)`
- `selected_boot_stdlib_word_inventory(...)` now optionally accepts `cases=` and
  can add per-word:
  - `impact_categories`
  - `impact_tags`
- `stdlib_impact_summary(...)` can now also add combined:
  - `impact_categories`
  - `impact_tags`
- `tools/mxportable.py --stdlib-manifest --show-impact`
  - human mode now prints impacted case category/tag summaries
  - JSON mode now carries the same joined inventory metadata

## Example commands

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word keep --show-impact
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word try --word ensure --show-impact --json
```

Typical human output now includes lines like:

```text
impact categories: stdlib=3
impact tags: combinators=3
```

## Why this matters

Rev275–rev281 already made it easy to answer:

1. which portability cases cover a word,
2. where the word lives in `core.mx`,
3. what it directly/transitively depends on,
4. which higher-level boot words use it,
5. which words/cases are impacted by a change, and
6. what exact command reruns that selected impact slice.

The missing interpretive question was the next tiny one:

> is this selected impact slice mostly combinators, cleanup contracts, aliases, or something else?

This rev answers that without inventing a richer dependency UI, new manifest
format, or scheduler. It simply rejoins already-explicit impacted case names
with the portability corpus Micromax already carries.

That means future Python/Rust/WASM hosts and future LLMs can now see both the
exact replay command *and* the shape of the affected contract slice without
manually re-querying the portability corpus by hand.
