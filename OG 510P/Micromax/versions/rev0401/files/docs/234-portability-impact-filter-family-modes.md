# Rev292 — explicit impact-filter family modes and transition metadata

## What landed

`mxportable --stdlib-manifest --show-impact` already exposed:

- exact impacted slices,
- exact replay commands,
- exact next-facet flag fragments, and
- exact full commands for the slice each visible facet would select.

Rev292 keeps that same tiny path, but makes one subtle thing explicit:

- whether choosing a facet **replaces** the current filter family, or
- whether it **appends** to the current family as a narrower conjunction.

Each `impact_filter_options` row now carries:

- `filter_family`
- `family_mode`
- `current_family_argv`
- `current_family_suffix`
- `effective_family_argv`
- `effective_family_suffix`

## Why this is useful

Rev291 already made every visible facet directly executable, but a future human or
future LLM still had to infer one last policy detail from behavior:

- is `--impact-word finally` a replacement pivot inside the impacted-word family?
- is `--impact-tag cleanup` an additive narrowing on top of the current tag slice?

That distinction matters when building one more refinement automatically.

Now the tool says that explicitly instead of forcing consumers to reverse-engineer
it from command strings.

## Current family semantics

The current `--show-impact` facet families behave like this:

- `impact-word` → `replace`
- `impact-distance` → `replace`
- `impact-category` → `replace`
- `impact-name` → `replace`
- `impact-tag` → `append`

So word/distance/category/name facets mean “pivot to exactly this same-family cut,”
while tag facets mean “keep the current tag slice and add this extra required tag.”

## Example

For the current slice:

```text
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors
```

A visible `cleanup` tag facet now carries metadata like:

```json
{
  "filter_family": "impact-tag",
  "family_mode": "append",
  "current_family_suffix": "--impact-tag errors",
  "effective_family_suffix": "--impact-tag errors --impact-tag cleanup"
}
```

But a visible `finally` impacted-word facet carries:

```json
{
  "filter_family": "impact-word",
  "family_mode": "replace",
  "current_family_suffix": "",
  "effective_family_suffix": "--impact-word finally"
}
```

Human output now also surfaces that distinction inline, for example:

```text
words: finally@1=3 [replace:--impact-word finally]
tags: cleanup=6 [append:--impact-tag cleanup => --impact-tag errors --impact-tag cleanup]
```

## Files touched

- `src/micromax/portability_suite.py`
- `tools/mxportable.py`
- `tests/test_portability_suite.py`
- `tests/test_mxcontext.py`

## Practical consequence

Future humans and future LLMs can now refine an impacted slice one step further
without guessing whether a facet is a same-family replacement or an additive
narrowing.
