# Rev290 — executable impact-filter facets

## What landed

`mxportable --stdlib-manifest --show-impact` already knew how to expose the
current impact slice plus the valid next filter facets for that slice.

Rev290 keeps the same tiny path, but removes one more manual step.

Each row in `impact_filter_options` now carries:

- `filter_argv`
- `filter_suffix`

for the exact facet row being shown.

That now applies to:

- impacted words
- shortest-path distances
- portability categories
- portability tags
- exact portability case names

## Why this is useful

Rev288 and rev289 made the impact slice self-discovering, but a human or future
LLM still had to translate a discovered option back into CLI flags by hand.

That was a small step, but it was still a lossy handoff.

Now the tool can say both:

- “these are the valid next cuts”
- “this is the exact flag sequence for each one”

without adding a scheduler, a new stateful workflow, or a larger dependency
model.

## Example

For a small slice like:

```text
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact
```

human output now shows things like:

```text
impact filter options:
  words: ensure@0=4 [--impact-word ensure], finally@1=4 [--impact-word finally]
  distances: 0(words=ensure,cases=4) [--impact-distance 0], 1(words=finally,cases=4) [--impact-distance 1]
  categories: stdlib=8 [--impact-category stdlib]
  tags: cleanup=8 [--impact-tag cleanup], errors=6 [--impact-tag errors]
```

And JSON now carries the same exact refinement data machine-readably:

```json
{
  "name": "finally",
  "distance": 1,
  "case_count": 4,
  "filter_argv": ["--impact-word", "finally"],
  "filter_suffix": "--impact-word finally"
}
```

## Files touched

- `src/micromax/portability_suite.py`
- `tools/mxportable.py`
- `tests/test_portability_suite.py`
- `tests/test_mxcontext.py`

## Practical consequence

Future humans and future LLMs can now move one notch faster from:

- “show me the impacted slice”
- to “show me the valid next cuts”
- to “re-run just that exact cut”

without reconstructing the flags themselves.
