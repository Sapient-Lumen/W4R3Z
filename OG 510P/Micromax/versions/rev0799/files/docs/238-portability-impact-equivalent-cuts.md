# Rev296 — show when different impact facets collapse to the same exact slice

## What changed

`mxportable --stdlib-manifest --show-impact` already exposed:

- the current impacted slice
- exact retest commands
- exact facet flag fragments
- exact full slice commands for each visible facet
- explicit family semantics (`replace` vs `append`)
- exact resulting-slice preview counts for each visible facet
- explicit preview effects/deltas telling whether a facet was a no-op or a real narrowing
- a small recommended-next-cut shortlist

Rev296 adds one more tiny layer to the same handoff surface: visible facet rows
now say when they are *equivalent* to another visible cut because they produce the
same exact impacted-word + impacted-case slice.

The shared helpers in `src/micromax/portability_suite.py` now derive:

- `equivalence_key`
- `equivalent_options`
- `equivalent_option_count`
- `has_equivalent_options`

Each equivalent option row keeps a tiny descriptor:

- `option_family`
- `option_label`
- `filter_suffix`
- `show_impact_command`

## Why this was the next honest tiny step

By rev295, a future human or future LLM could already see:

- which facets were no-ops
- which facets were narrower
- how much each narrower cut would reduce the current slice
- which coarse cuts were the best next ones to try first

But one small operational question still required visual comparison or trial
commands:

- “Are these two recommendations actually different?”
- “Do `--impact-word finally` and `--impact-distance 1` narrow to the same slice?”
- “Should I rerun both of these, or are they interchangeable?”

Rev296 keeps the answer tiny and inspectable instead of inventing a scheduler or
more opinionated planner.

## Human CLI surface

Human output keeps the existing facet inventory and recommendation shortlist, but
now annotates rows with `same-result: ...` when another visible cut lands on the
same exact slice:

```text
recommended:
  2. words: finally@1=3 [replace:--impact-word finally; delta:w-1,c-3,d-1; result:w=1,c=3,d=1; same-result: distances:1, tags:aliases]
  4. distances: 1(words=finally,cases=3) [replace:--impact-distance 1; delta:w-1,c-3,d-1; result:w=1,c=3,d=1; same-result: tags:aliases, words:finally]
  5. tags: aliases=3 [append:--impact-tag aliases => --impact-tag errors --impact-tag aliases; delta:w-1,c-3,d-1; result:w=1,c=3,d=1; same-result: distances:1, words:finally]
```

That keeps the full facet inventory available, but makes interchangeable next
cuts obvious.

## JSON surface

Example shape for the new equivalence metadata:

```json
{
  "option_family": "words",
  "option_label": "finally",
  "equivalent_option_count": 2,
  "equivalent_options": [
    {
      "option_family": "distances",
      "option_label": "1",
      "filter_suffix": "--impact-distance 1"
    },
    {
      "option_family": "tags",
      "option_label": "aliases",
      "filter_suffix": "--impact-tag aliases"
    }
  ]
}
```

So a future host or future LLM can now distinguish “another good narrowing” from
“the same narrowing expressed through a different family”.

## Implementation notes

Shared helpers:

- `impact_filter_option_label(...)`
- `stdlib_impact_filter_equivalence_key(...)`
- `annotate_stdlib_impact_filter_option_equivalences(...)`

Implementation strategy:

- derive a stable preview key from `preview_impact_words` + `preview_impact_case_names`
- group visible facet rows by that preview key
- attach the other rows in the same group as `equivalent_options`
- let recommended rows inherit that metadata so the shortlist stays tiny but
  still explains interchangeable cuts

This keeps the equivalence logic local to the already visible slice instead of
adding a planner.

## Focused validation

Covered in:

- `tests/test_portability_suite.py`
- `tests/test_mxcontext.py`

The focused assertions pin down both the JSON equivalence metadata and the
updated human CLI formatting for the `ensure` + `errors` slice.
