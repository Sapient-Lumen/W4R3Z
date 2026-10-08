# Rev288: expose next-step impacted-word / depth filter options for selected slices

Rev287 made selected boot-stdlib impact slices directly filterable by impacted
word, shortest-path depth, and semantic portability case metadata, but it still
left one tiny discovery step to humans and future LLMs.

`--show-impact` could already answer:

- which impacted boot-stdlib words are downstream of a selected word,
- which exact portability cases belong to each impacted word,
- what shortest stdlib paths and distances explain that impact,
- what exact replay command reruns each impacted group and stage, and
- how to cut that payload down with exact `--impact-*` filters.

The missing next question was:

> before I guess another filter, what are the valid next `--impact-word` and
> `--impact-distance` cuts for the slice I already have?

Rev288 keeps that next step tiny.

## What changed

- `src/micromax/portability_suite.py` now also provides:
  - `stdlib_impact_filter_options(...)`
- `stdlib_impact_slice(...)` now carries:
  - `impact_filter_options`
- each selected row and the combined `impact_summary` now expose:
  - `impact_filter_options.words`
  - `impact_filter_options.distances`
- `tools/mxportable.py --stdlib-manifest --show-impact` now prints those
  options in human mode too.

## Shape

The new helper does not invent a second dependency graph.

It simply summarizes the already-selected impact groups into small valid next
cuts:

- `words`: one row per currently visible impacted word
  - `name`
  - `distance`
  - `case_count`
- `distances`: one row per currently visible shortest-path depth
  - `distance`
  - `words`
  - `word_count`
  - `case_count`

Because this is derived *after* any active `--impact-word`, `--impact-distance`,
`--impact-category`, `--impact-tag`, `--impact-name`, or
`--impact-name-contains` filters, it stays honest about the slice you are
actually looking at.

## Examples

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word keep --show-impact
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-name-contains cleanup-error-wins --json
```

Human output can now say things like:

```text
impact filter options:
  words: keep@0=1, bi@1=1, tri@1=1
  distances: 0(words=keep,cases=1), 1(words=bi,tri,cases=2)
```

Or, for an already-filtered semantic slice:

```text
impact filters: tags=errors

impact filter options:
  words: ensure@0=3, finally@1=3
  distances: 0(words=ensure,cases=3), 1(words=finally,cases=3)
```

JSON now carries the same structure directly under each row and the combined
summary, so a future host or future LLM can see the remaining valid word/depth
cuts without scraping human text or reconstructing them from paths and cases.

## Why this helps

The recent portability/tooling thread now becomes slightly more self-discovering:

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
13. structured next-step filter options.

So a future host or future LLM can now move from “this word changed” to a full
replay plan, one semantic slice, and then one exact valid next word/depth cut
without guessing what filters remain meaningful for the slice already on screen.
