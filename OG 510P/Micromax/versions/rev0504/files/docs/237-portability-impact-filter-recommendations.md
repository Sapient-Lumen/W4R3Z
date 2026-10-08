# Rev295 — recommend the best next narrowing cuts instead of making users rank every facet

## What changed

`mxportable --stdlib-manifest --show-impact` already exposed:

- the current impacted slice
- exact retest commands
- exact facet flag fragments
- exact full slice commands for each visible facet
- explicit family semantics (`replace` vs `append`)
- exact resulting-slice preview counts for each visible facet
- explicit preview effects/deltas telling whether a facet was a no-op or a real narrowing

Rev295 adds one more tiny layer to the same handoff surface: the shared
`impact_filter_options` payload now also carries a small `recommended` shortlist
that points at the best *real narrower* next cuts for the current slice.

The shared helpers in `src/micromax/portability_suite.py` now derive a ranked
shortlist by:

- ignoring facets that are a no-op for the current slice
- ignoring facets that do not actually reduce words/cases/stages
- preferring genuinely narrower cuts
- preferring coarser reusable families (`words`, `distances`, `tags`, `categories`)
  before exact one-case `names` cuts
- then ranking by case/word/stage reduction and resulting slice size

Each recommended row keeps the same full metadata as the ordinary facet row and
also carries:

- `option_family`
- `option_label`
- `recommendation_rank`

## Why this was the next honest tiny step

By rev294, a future human or future LLM could already see:

- which facets were no-ops
- which facets were narrower
- how much each narrower cut would reduce the current slice

But one last operational step still required hand-sorting the visible facet
list:

- “Which narrower cut should I try first?”
- “What is the best coarse cut before I jump down to exact case names?”
- “Which next cut is most likely to shrink this slice meaningfully without
  overfitting to one exact case?”

Rev295 keeps that answer tiny and inspectable instead of inventing a scheduler
or planner.

## Human CLI surface

Human output still prints the full facet inventory, but now also prints a small
recommended shortlist for the current slice:

```text
impact filter options:
  words: ensure@0=3 [...snip...]
  distances: 0(words=ensure,cases=3) [...snip...]
  tags: aliases=3 [...snip...]
  names: stdlib-ensure-cleanup-error-wins-on-success[words=ensure;depths=0] [...snip...]
  recommended:
    1. words: ensure@0=3 [replace:--impact-word ensure; delta:w-1,c-3,d-1; result:w=1,c=3,d=1]
    2. words: finally@1=3 [replace:--impact-word finally; delta:w-1,c-3,d-1; result:w=1,c=3,d=1]
    3. distances: 0(words=ensure,cases=3) [replace:--impact-distance 0; delta:w-1,c-3,d-1; result:w=1,c=3,d=1]
    4. distances: 1(words=finally,cases=3) [replace:--impact-distance 1; delta:w-1,c-3,d-1; result:w=1,c=3,d=1]
    5. tags: aliases=3 [append:--impact-tag aliases => --impact-tag errors --impact-tag aliases; delta:w-1,c-3,d-1; result:w=1,c=3,d=1]
```

That keeps the full facet inventory available, but gives humans and future LLMs
a tiny “start here” path without hiding the underlying data.

## JSON surface

Example shape for the new shortlist:

```json
{
  "recommended": [
    {
      "recommendation_rank": 1,
      "option_family": "words",
      "option_label": "ensure",
      "filter_suffix": "--impact-word ensure",
      "preview_effect": "narrower",
      "preview_impact_case_delta": -3,
      "show_impact_command": "PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word ensure --impact-tag errors"
    }
  ],
  "recommended_count": 5
}
```

So a future host or future LLM can now grab the best few real next narrows
directly instead of ranking all candidate facets itself.

## Implementation notes

Shared helper:

- `stdlib_recommended_impact_filter_options(...)`

Recommendation strategy:

- start from the already derived `impact_filter_options` rows
- keep only real narrower cuts (`preview_changes_slice` plus some actual
  reduction)
- prefer coarser structural/semantic families before exact single-case name cuts
- keep the shortlist tiny (`5`) so the output stays inspectable

This keeps the recommendation logic local to the already visible slice instead
of adding a second planner.

## Focused validation

Covered in:

- `tests/test_portability_suite.py`
- `tests/test_mxcontext.py`

The focused assertions pin down both the JSON shortlist and the updated human
CLI formatting, including the coarse-first ordering for the `ensure` +
`errors` slice.
