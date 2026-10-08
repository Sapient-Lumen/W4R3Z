# Rev294 — make facet previews say whether they are a no-op or a real narrowing

## What changed

`mxportable --stdlib-manifest --show-impact` already exposed:

- the current impacted slice
- exact retest commands
- exact facet flag fragments
- exact full slice commands for each visible facet
- explicit family semantics (`replace` vs `append`)
- exact resulting-slice preview counts for each visible facet

Rev294 adds one more tiny layer to the same handoff surface: each visible
facet row now also says whether taking that cut would actually change the
slice, and by how much.

The shared helpers in `src/micromax/portability_suite.py` now derive:

- `preview_is_current_slice`
- `preview_changes_slice`
- `preview_effect`
- `preview_impact_word_delta`
- `preview_impact_case_delta`
- `preview_impact_stage_delta`
- `preview_impact_word_reduction`
- `preview_impact_case_reduction`
- `preview_impact_stage_reduction`

Those effect/delta fields are attached to every row inside
`impact_filter_options` (`words`, `distances`, `categories`, `tags`, and
`names`).

## Why this was the next honest tiny step

By rev293, a future human or future LLM could already see how large the next
candidate slice would be.

But one last operational question still required manual comparison or another
command:

- “Is this a real narrowing or just the current slice again?”
- “Does choosing this active tag actually change anything?”
- “How much smaller is this cut relative to the slice I already have?”

Rev294 keeps that answer tiny and inspectable instead of inventing a richer
planner.

## Human CLI surface

Human output still prints the same facet inventory, but now preview text can
also say whether a cut is a no-op and how much it narrows the current slice:

```text
impact filter options:
  words: ensure@0=3 [replace:--impact-word ensure; delta:w-1,c-3,d-1; result:w=1,c=3,d=1]
  tags: cleanup=6 [append:--impact-tag cleanup => --impact-tag errors --impact-tag cleanup; same-slice; result:w=2,c=6,d=2]
  tags: errors=6 [append:--impact-tag errors; same-slice; result:w=2,c=6,d=2]
```

Where:

- `same-slice` means the facet is a no-op from the current filtered slice
- `delta:w-1,c-3,d-1` means the candidate cut removes 1 impacted word, 3
  impacted portability cases, and 1 replay stage from the current slice
- `result:w=...,c=...,d=...` still reports the resulting slice size

## JSON surface

Example shape for one active facet row:

```json
{
  "name": "errors",
  "filter_suffix": "--impact-tag errors",
  "family_mode": "append",
  "preview_is_current_slice": true,
  "preview_changes_slice": false,
  "preview_effect": "same-slice",
  "preview_impact_word_delta": 0,
  "preview_impact_case_delta": 0,
  "preview_impact_stage_delta": 0,
  "preview_impact_word_count": 2,
  "preview_impact_case_count": 6,
  "preview_impact_stage_count": 2
}
```

And one narrower facet row now looks like:

```json
{
  "name": "ensure",
  "filter_suffix": "--impact-word ensure",
  "preview_effect": "narrower",
  "preview_impact_word_delta": -1,
  "preview_impact_case_delta": -3,
  "preview_impact_stage_delta": -1,
  "preview_impact_word_count": 1,
  "preview_impact_case_count": 3,
  "preview_impact_stage_count": 1
}
```

So a future host or future LLM can now distinguish an active/no-op facet from a
real narrowing without diffing the counts manually.

## Implementation notes

Shared helper:

- `stdlib_impact_preview_delta_fields(...)`

Preview-effect strategy:

- compare the candidate facet preview against the current slice preview already
  visible in the same `impact_filter_options` block
- treat exact same word/case lists as `same-slice`
- derive signed deltas for impacted-word / case / stage counts
- classify count-only changes conservatively as `narrower`, `broader`,
  `same-size-pivot`, or `mixed`

This keeps the decision aid local to the already selected slice instead of
adding a second planner or a scheduler.

## Focused validation

Covered in:

- `tests/test_portability_suite.py`
- `tests/test_mxcontext.py`

The focused assertions pin down both the new JSON metadata and the updated human
CLI formatting, including active-tag no-op behavior.
