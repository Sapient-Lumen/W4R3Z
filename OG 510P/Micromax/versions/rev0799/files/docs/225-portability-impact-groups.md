# Rev283: expose grouped impact provenance for selected boot-stdlib slices

Rev282 made selected change impact more descriptive, but there was still one tiny
"why this exact case?" gap left for humans and future LLMs.

`--show-impact` could already answer:

- which impacted boot-stdlib words are downstream of a selected word,
- which portability cases cover that downstream slice,
- which categories/tags describe the combined slice, and
- which exact replay command reruns the whole impacted set.

The missing step was provenance inside that combined slice. A user still had to
mentally answer questions like:

> Is `stdlib-bi` here because I selected `keep`, or because I selected `bi`
> directly too?
>
> Which exact impacted word contributes these four cleanup cases?
>
> What is the shortest stdlib path from the changed word to that impacted word?

Rev283 fills that gap with one tiny machine-readable grouping layer.

## What changed

- `src/micromax/portability_suite.py` now also provides:
  - `boot_stdlib_impact_paths(...)`
  - `stdlib_impact_groups(...)`
  - `merge_stdlib_impact_groups(...)`
- `selected_boot_stdlib_word_inventory(...)` now adds per selected word:
  - `impact_groups`
- `stdlib_impact_summary(...)` now also adds combined:
  - `impact_groups`
- `tools/mxportable.py --stdlib-manifest --show-impact`
  - human mode now prints grouped impacted words with shortest paths and exact
    case names
  - JSON mode now carries the same grouped provenance payload

## Shape

Each `impact_groups` row names one impacted boot-stdlib word and carries:

- `word`
- `selected_words`
- `paths`
- `case_names`
- `case_count`
- `line`
- `stack_effect`
- `alias_of`
- optional joined `categories` / `tags`

That keeps the payload small, inspectable, and easy to evolve by hand.

## Example

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word keep --show-impact
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --word finally --show-impact --json
```

Human output now includes tiny provenance lines like:

```text
impact groups:
  keep <= keep :: stdlib-keep
  bi <= keep -> bi :: stdlib-bi
  tri <= keep -> tri :: stdlib-tri
```

And merged selections can show multiple roots/paths for the same impacted word,
for example `finally <= ensure -> finally | finally`.

## Why this helps

This keeps the current portability tooling on the same tiny-inspectable track as
recent revs:

1. manifest coverage,
2. source inventory,
3. dependency inventory,
4. closure inventory,
5. reverse-user inventory,
6. impact inventory,
7. exact retest commands,
8. grouped impact provenance.

So a future host or future LLM can now answer all of these from one shared
surface instead of ad hoc graph-reading:

- what changed,
- what depends on it,
- what contract slice is touched,
- what exact cases should rerun,
- and why each case is in that set.
