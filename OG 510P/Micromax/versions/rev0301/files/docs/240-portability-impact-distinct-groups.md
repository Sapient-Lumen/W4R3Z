# Rev298 — make distinct next cuts self-contained by grouping their absorbed alternatives

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
- a deduped `recommended_distinct` shortlist that kept one representative cut per same-result slice

Rev298 adds one more tiny layer to that same handoff surface: the distinct
shortlist is now self-contained. Each distinct recommendation now carries the
recommended options it absorbed, and the shared JSON payload also publishes a
small `recommended_distinct_groups` view that makes the representative-plus-
alternatives structure explicit.

The shared helpers in `src/micromax/portability_suite.py` now derive:

- `represented_options`
- `represented_alternatives`
- `recommended_distinct_groups`
- `recommended_distinct_group_count`

## Why this was the next honest tiny step

By rev297, a future human or future LLM could already see:

- which recommendations were interchangeable
- which distinct representative was chosen for each exact slice
- which visible facets were same-result equivalents

But one small inference still required hopping between lists:

- “Which ranked recommendations did this distinct representative absorb?”
- “Does `words:finally` stand in for `distance:1`, `tag:aliases`, or both?”
- “Can I stay inside the deduped shortlist and still explain the alternatives?”

Rev298 keeps the answer tiny and inspectable: preserve the full ranked
`recommended` list, keep the compact `recommended_distinct` shortlist, and add a
small grouped view so the representative and the alternatives it covers are
visible in one place.

## Human CLI surface

Human output keeps the existing full recommendation list, but now also gives the
distinct shortlist a tiny “covers” hint plus an explicit grouped block:

```text
recommended distinct:
  1. words: ensure@0=3 [...] [covers: distances:0]
  2. words: finally@1=3 [...] [covers: distances:1, tags:aliases]
recommended distinct groups:
  1. words: ensure
     alternatives: distances:0
  2. words: finally
     alternatives: distances:1, tags:aliases
```

That keeps the ranked shortlist terse while giving future humans/LLMs a
self-contained explanation of what each distinct cut stands for.

## JSON surface

Example shape for the new grouped view:

```json
{
  "recommended_distinct_count": 2,
  "recommended_distinct_group_count": 2,
  "recommended_distinct": [
    {
      "recommendation_rank": 1,
      "option_family": "words",
      "option_label": "ensure",
      "represented_alternatives": [
        {"option_family": "distances", "option_label": "0"}
      ]
    }
  ],
  "recommended_distinct_groups": [
    {
      "recommendation_rank": 2,
      "representative": {
        "option_family": "words",
        "option_label": "finally"
      },
      "represented_alternatives": [
        {"option_family": "distances", "option_label": "1"},
        {"option_family": "tags", "option_label": "aliases"}
      ]
    }
  ]
}
```

So a future host or future LLM can now answer both:

- “what are the distinct next cuts?” and
- “which other recommended cuts does each one stand in for?”

without rebuilding that relationship from two separate lists.

## Implementation notes

Shared helpers:

- `impact_filter_option_summary(...)`
- `stdlib_distinct_impact_filter_options(...)`
- `stdlib_distinct_impact_filter_groups(...)`

Implementation strategy:

- keep the existing ranked `recommended` list intact
- keep using rev296's same-result equivalence key
- enrich each distinct row with the recommended options it represents
- publish one tiny grouped view keyed by the already-ranked representative

This keeps the new behavior local to the existing recommendation surface instead
of adding a planner.

## Focused validation

Covered in:

- `tests/test_portability_suite.py`
- `tests/test_mxcontext.py`

The focused assertions pin down the new `represented_*` fields on distinct rows,
the grouped JSON payload, and the updated human CLI formatting for the
`ensure` + `errors` slice.
