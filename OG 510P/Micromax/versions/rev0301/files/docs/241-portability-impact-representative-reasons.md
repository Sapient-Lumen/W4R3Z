# rev299: impact representatives explain why they won

## What changed

`mxportable --stdlib-manifest --show-impact` already exposed:

- the full visible impact facet inventory
- ranked `recommended` next cuts
- deduped `recommended_distinct` representatives
- grouped `recommended_distinct_groups` showing which alternatives each representative absorbed

Rev299 adds one more tiny handoff layer: each distinct representative now carries
`representative_reason_code`, `representative_reason`,
`represented_alternative_labels`, and `represented_alternative_families`.
The current grouped payload mirrors the same fields.

That means a future human or future LLM no longer has to infer *why* `words:finally`
was kept as the representative while `distances:1` and `tags:aliases` were absorbed.
The payload now says that directly.

## Current reason shapes

- `only-option`
  - this representative is the only visible distinct cut for that exact slice
- `coarser-family`
  - this representative wins because it belongs to a coarser, more reusable filter family
    than the equivalent alternatives
- `same-family-earlier-rank`
  - this representative wins because equivalent options stayed in the same family and this
    one ranked first
- `mixed-family-earlier-rank`
  - fallback when the winning representative beat a mixed set of alternatives and simple
    family priority was not the whole story

Today the real `ensure --impact-tag errors` slice now explains itself like this:

- `words:ensure`
  - preferred as the coarsest equivalent cut over `distances:0`
- `words:finally`
  - preferred as the coarsest equivalent cut over `distances:1`, `tags:aliases`

## Why this was the next honest tiny step

Recent revs already made the impact surface exact, replayable, previewable, deduped,
and grouped. The last manual inference step was still: “why did the tool keep *this*
representative instead of one of the interchangeable alternatives?” Rev299 keeps the
same tiny inspectable path and answers that question directly instead of adding a larger
planner or scheduler.

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
