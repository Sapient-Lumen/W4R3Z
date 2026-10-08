# Rev289: expose semantic next-step impact filter options for selected slices

Rev288 made selected boot-stdlib impact slices directly self-discovering for
impacted words and shortest-path depths, but it still left one semantic
inspection step to humans and future LLMs.

`--show-impact` could already answer:

- which impacted boot-stdlib words are downstream of a selected word,
- which exact portability cases belong to each impacted word,
- what shortest stdlib paths and distances explain that impact,
- what exact replay command reruns each impacted group and stage,
- how to cut that payload down with exact `--impact-word` / `--impact-distance`
  filters, and
- how to cut that payload down semantically with exact
  `--impact-category` / `--impact-tag` / `--impact-name` filters.

The missing next question was:

> before I guess another semantic filter, what are the valid next
> `--impact-category`, `--impact-tag`, and exact `--impact-name` cuts for the
> slice I already have?

Rev289 keeps that next step tiny.

## What changed

- `src/micromax/portability_suite.py` now extends:
  - `stdlib_impact_filter_options(...)`
- each selected row and the combined `impact_summary` now also expose:
  - `impact_filter_options.categories`
  - `impact_filter_options.tags`
  - `impact_filter_options.names`
- `tools/mxportable.py --stdlib-manifest --show-impact` now prints those
  semantic options in human mode too.

## Shape

The helper still does not invent a second dependency graph or a second semantic
index.

It simply summarizes the already-selected impact groups into small valid next
semantic cuts:

- `categories`: one row per currently visible portability category
  - `name`
  - `count`
- `tags`: one row per currently visible portability tag
  - `name`
  - `count`
- `names`: one row per currently visible exact portability case name
  - `name`
  - `words`
  - `word_count`
  - `distances`
  - `distance_count`

Because this is derived *after* any active `--impact-word`, `--impact-distance`,
`--impact-category`, `--impact-tag`, `--impact-name`, or
`--impact-name-contains` filters, it stays honest about the exact slice you are
already looking at.

## Examples

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-distance 1 --json
```

Human output can now say things like:

```text
impact filter options:
  words: ensure@0=4, finally@1=4
  distances: 0(words=ensure,cases=4), 1(words=finally,cases=4)
  categories: stdlib=8
  tags: aliases=4, cleanup=8, errors=6
  names: stdlib-ensure-success-runs-cleanup[words=ensure;depths=0], ...
```

Or, for an already-filtered semantic slice:

```text
impact filters: tags=errors

impact filter options:
  words: ensure@0=3, finally@1=3
  distances: 0(words=ensure,cases=3), 1(words=finally,cases=3)
  categories: stdlib=6
  tags: aliases=3, cleanup=6, errors=6
  names: stdlib-ensure-failure-reraises-after-cleanup[words=ensure;depths=0], ...
```

JSON carries the same structure directly under each row and the combined
summary, so a future host or future LLM can see the remaining valid semantic
cuts without scraping human text or reconstructing tag/category/name inventories
from the raw cases.

## Why this helps

The recent portability/tooling thread now becomes a little more faceted without
becoming heavier:

1. manifest coverage,
2. source inventory,
3. dependency inventory,
4. closure inventory,
5. reverse-user inventory,
6. impact inventory,
7. exact combined retest commands,
8. grouped impact provenance,
9. per-group replay metadata,
10. staged replay plans,
11. impacted-word / depth filters,
12. semantic case filters,
13. structured next-step word/depth filter options,
14. structured next-step semantic filter options.

So a future host or future LLM can now move from “this word changed” to a full
replay plan, one semantic slice, one exact valid next word/depth cut, and then
one exact valid category/tag/name cut without guessing what filters remain
meaningful for the slice already on screen.
