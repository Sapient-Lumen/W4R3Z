# Rev293 — preview the resulting slice for each impact facet

## What changed

`mxportable --stdlib-manifest --show-impact` already exposed:

- the current impacted slice
- exact rerun commands
- exact next-step filter fragments
- exact full slice commands for each visible facet
- explicit family semantics (`replace` vs `append`)

Rev293 adds one more tiny layer to the same handoff surface: each visible
facet row now carries a compact preview of the slice you would get if you took
that cut.

The shared helpers in `src/micromax/portability_suite.py` now derive:

- `preview_impact_words`
- `preview_impact_word_count`
- `preview_impact_case_names`
- `preview_impact_case_count`
- `preview_impact_group_count`
- `preview_impact_stage_count`

Those preview fields are attached to every row inside
`impact_filter_options` (`words`, `distances`, `categories`, `tags`, and
`names`).

## Why this was the next honest tiny step

By rev292, a future human or future LLM could already see:

- which facets were valid for the current slice
- which command each facet implied
- whether choosing that facet would replace a same-family filter or append to a
  conjunctive family like `--impact-tag`

But one last decision still required either running another command or mentally
simulating the slice:

- “Which cut is the smallest useful next replay?”
- “Does this facet collapse me to one word or keep two?”
- “Will this produce one stage or still require a two-stage replay?”

Rev293 keeps that answer tiny and inspectable instead of inventing a richer
planner.

## Human CLI surface

Human output still prints the same facet inventory, but each row now includes a
compact preview suffix:

```text
impact filter options:
  words: ensure@0=4 [replace:--impact-word ensure; result:w=1,c=4,d=1], finally@1=4 [replace:--impact-word finally; result:w=1,c=4,d=1]
  tags: errors=6 [append:--impact-tag errors; result:w=2,c=6,d=2], cleanup=8 [append:--impact-tag cleanup; result:w=2,c=8,d=2]
```

Where:

- `w` = resulting impacted word count
- `c` = resulting portability case count
- `d` = resulting stage/depth count

That is intentionally small enough to stay readable in a terminal while still
answering the next operational question.

## JSON surface

Example shape for one facet row:

```json
{
  "name": "finally",
  "filter_suffix": "--impact-word finally",
  "family_mode": "replace",
  "show_impact_command": "PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word finally",
  "preview_impact_words": ["finally"],
  "preview_impact_word_count": 1,
  "preview_impact_case_names": [
    "stdlib-finally-success-runs-cleanup",
    "stdlib-finally-failure-reraises-after-cleanup",
    "stdlib-finally-cleanup-error-wins-on-success",
    "stdlib-finally-cleanup-error-wins-on-failure"
  ],
  "preview_impact_case_count": 4,
  "preview_impact_group_count": 1,
  "preview_impact_stage_count": 1
}
```

So a future host or future LLM can now choose between candidate refinements
without executing each command just to inspect the resulting cardinality.

## Implementation notes

Shared helper:

- `stdlib_impact_preview_fields(...)`

Preview generation strategy:

- word / distance rows preview by reselecting the current impacted groups with
  `select_stdlib_impact_groups(...)`
- category / tag / name rows preview by refiltering the current groups through
  `refilter_stdlib_impact_groups(...)`
- name previews also work without the full case corpus by falling back to exact
  group-local case-name trimming

This keeps preview computation local to the already selected slice instead of
adding a second planner or scheduler.

## Focused validation

Covered in:

- `tests/test_portability_suite.py`
- `tests/test_mxcontext.py`

The focused assertions pin down both the new JSON metadata and the updated human
CLI formatting.
