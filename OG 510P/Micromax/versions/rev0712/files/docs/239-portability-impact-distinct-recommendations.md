# Rev297 — dedupe equivalent next-cut recommendations down to one representative slice

## What changed

`mxportable --stdlib-manifest --show-impact` already exposed:

- the current impacted slice
- exact retest commands
- exact facet flag fragments
- exact full slice commands for each visible facet
- explicit family semantics (`replace` vs `append`)
- exact resulting-slice preview counts for each visible facet
- explicit preview effects/deltas telling whether a facet was a no-op or a real narrowing
- a small ranked `recommended` shortlist
- same-result equivalence metadata for interchangeable cuts

Rev297 adds one more tiny layer to that same handoff surface: a deduped
`recommended_distinct` shortlist that keeps only one representative cut per exact
same-result slice.

The shared helpers in `src/micromax/portability_suite.py` now derive:

- `recommended_distinct`
- `recommended_distinct_count`
- a tiny helper `stdlib_distinct_impact_filter_options(...)`

## Why this was the next honest tiny step

By rev296, a future human or future LLM could already see:

- which recommendations were interchangeable
- which options were no-ops
- which options were narrower
- how much each narrower cut would reduce the current slice

But one small operational step still required visual deduping by hand:

- “Which single cut should I actually take for this slice?”
- “Do I need both `--impact-word finally` and `--impact-distance 1` in the shortlist?”
- “Can the shortlist stay coarse without losing exactness?”

Rev297 keeps the answer tiny and inspectable: preserve the full recommendation
list for transparency, but also publish one distinct-next-cut list that picks the
first ranked representative from each equivalence class.

## Human CLI surface

Human output keeps the existing full recommendation list, but now also prints a
smaller `recommended distinct:` block:

```text
recommended:
  1. words: ensure@0=3 [... same-result: distances:0]
  2. words: finally@1=3 [... same-result: distances:1, tags:aliases]
  3. distances: 0(words=ensure,cases=3) [... same-result: words:ensure]
  4. distances: 1(words=finally,cases=3) [... same-result: tags:aliases, words:finally]
  5. tags: aliases=3 [... same-result: distances:1, words:finally]
recommended distinct:
  1. words: ensure@0=3 [... same-result: distances:0]
  2. words: finally@1=3 [... same-result: distances:1, tags:aliases]
```

That keeps the fully ranked shortlist visible for debugging, while giving future
humans/LLMs the one-line answer to “what are the distinct next cuts?”

## JSON surface

Example shape for the new deduped shortlist:

```json
{
  "recommended_count": 5,
  "recommended_distinct_count": 2,
  "recommended_distinct": [
    {
      "recommendation_rank": 1,
      "option_family": "words",
      "option_label": "ensure"
    },
    {
      "recommendation_rank": 2,
      "option_family": "words",
      "option_label": "finally"
    }
  ]
}
```

So a future host or future LLM can now choose one representative narrowing per
exact slice without throwing away the richer full recommendation inventory.

## Implementation notes

Shared helpers:

- `stdlib_recommended_impact_filter_options(...)`
- `stdlib_distinct_impact_filter_options(...)`

Implementation strategy:

- keep the existing ranked `recommended` list intact
- collapse that already-ranked shortlist by rev296's equivalence key
- preserve the first-ranked representative from each same-result group
- renumber the resulting `recommended_distinct` rows from 1

This keeps the new behavior local to the existing recommendation surface instead
of adding a planner.

## Focused validation

Covered in:

- `tests/test_portability_suite.py`
- `tests/test_mxcontext.py`

The focused assertions pin down both the JSON `recommended_distinct` payload and
the updated human CLI formatting for the `ensure` + `errors` slice.
