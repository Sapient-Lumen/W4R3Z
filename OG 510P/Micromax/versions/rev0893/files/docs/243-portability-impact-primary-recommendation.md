# Portability impact primary recommendation (rev301)

Rev301 adds one tiny operational layer on top of the existing `mxportable --stdlib-manifest --show-impact` recommendation surfaces: the tool now exposes the single best next cut directly, instead of making a human or future LLM read the ranked shortlist and pick the first distinct representative by hand.

## What changed

The shared impact-filter payload now carries:

- `recommended_primary`
- `recommended_primary_group`
- `recommended_primary_command`
- `recommended_primary_json_command`

`recommended_primary` is the first row from `recommended_distinct` when a deduped shortlist exists, falling back to the first row from the full ranked `recommended` list when it does not. That keeps the "best next cut" aligned with the already-established policy:

- only real narrows
- coarser reusable families before exact case-name cuts
- one representative cut per exact resulting slice

`recommended_primary_group` mirrors the grouped distinct view for that same representative, so future hosts and future LLMs can see the same alternatives, ranks, and representative-reason metadata without scanning the rest of the payload.

## Why this is useful

By rev300 the tool already knew:

- the impacted words/cases/stages
- exact rerun commands
- exact facet flags
- family replace-vs-append semantics
- preview sizes and signed deltas
- equivalent cuts
- ranked recommendations
- distinct grouped recommendations
- representative reasons and full-list rank coverage

The last small manual step was still: “which exact command should I paste first?” Rev301 makes that answer explicit.

## Example

For:

```text
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors
```

The tool now surfaces a primary next cut equivalent to:

```text
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word ensure --impact-tag errors
```

That recommendation stays aligned with the distinct shortlist and grouped view:

- representative: `words:ensure`
- absorbed alternative: `distances:0`
- covered shortlist ranks: `1,3`
- representative reason: preferred as the coarsest equivalent cut

## Human CLI surface

Human `--show-impact` output now includes:

- `recommended next: ...`
- the exact full `command: ...` line for that next cut

That keeps the operational answer visible without replacing the fuller `recommended`, `recommended distinct`, or `recommended distinct groups` sections.

## Files touched

- `src/micromax/portability_suite.py`
- `tools/mxportable.py`
- `tests/test_portability_suite.py`
- `tools/mxcontext.py`
- `tests/test_mxcontext.py`

## Focused validation

Rev301 focused validation covered:

- recommendation payload tests in `tests/test_portability_suite.py`
- human CLI recommendation rendering in `tests/test_portability_suite.py`
- `tests/test_try_combinator.py`
- `tests/test_vm_rev11.py`
- `python tools/mxcontext.py --json --check`
