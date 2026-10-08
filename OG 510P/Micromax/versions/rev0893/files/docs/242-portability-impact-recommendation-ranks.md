# rev300: distinct impact cuts now remember their source ranks

## What changed

`mxportable --stdlib-manifest --show-impact` already exposed:

- the full ranked `recommended` shortlist
- deduped `recommended_distinct` representatives
- grouped `recommended_distinct_groups` showing absorbed alternatives
- representative-reason metadata explaining *why* one equivalent cut won

Rev300 adds one more tiny handoff layer: distinct rows and groups now also carry
`source_recommendation_rank`, `represented_recommendation_ranks`,
`represented_alternative_ranks`, `represented_rank_min`, and
`represented_rank_max`. Human output now mirrors that with compact
`full ranks: ...` hints.

That means a future human or future LLM no longer has to jump back to the full
ranked shortlist to answer questions like:

- “Did this representative absorb only the next rank, or several later ones?”
- “Was `words:finally` originally rank 2 and did it also absorb ranks 4 and 5?”

The payload now says that directly.

## Example

Today the real `ensure --impact-tag errors` slice now explains itself like this:

- `words:ensure`
  - `source_recommendation_rank = 1`
  - `represented_recommendation_ranks = [1, 3]`
- `words:finally`
  - `source_recommendation_rank = 2`
  - `represented_recommendation_ranks = [2, 4, 5]`

So the deduped shortlist is no longer just “one representative per slice”; it is
now also a tiny map back to the full shortlist positions that representative
stands for.

## Why this was the next honest tiny step

Recent revs already made the impact surface exact, replayable, previewable,
recommended, deduped, grouped, and self-explaining. The last manual jump was
still: “where did the absorbed alternatives sit in the original ranked list?”
Rev300 keeps the same tiny inspectable path and answers that question directly
instead of widening into a planner or scheduler.

## Useful checks

Human output:

```bash
PYTHONPATH=src python tools/mxportable.py \
  --stdlib-manifest --word ensure --show-impact --impact-tag errors
```

JSON output:

```bash
PYTHONPATH=src python tools/mxportable.py \
  --stdlib-manifest --word ensure --show-impact --impact-tag errors --json
```

Focused tests:

```bash
pytest -q tests/test_portability_suite.py -k 'recommended or show_impact or preserve_current_tag_slice_in_json'
pytest -q tests/test_mxcontext.py
```
