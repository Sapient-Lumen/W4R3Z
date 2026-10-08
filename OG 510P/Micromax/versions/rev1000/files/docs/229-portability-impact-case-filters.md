# Rev287: filter selected boot-stdlib impact slices by portability case metadata

Rev286 made selected change impact sliceable by impacted word and shortest-path
stage, but it still left one tiny manual step for humans and future LLMs.

`--show-impact` could already answer:

- which impacted boot-stdlib words are downstream of a selected word,
- which exact portability cases belong to each impacted word,
- what shortest stdlib paths explain that impact,
- what exact replay command reruns each impacted word and staged slice, and
- how to trim that payload to one exact impacted word or one shortest-path depth.

The missing next question was:

> can I ask for only the `errors` cases, only the cleanup-error cases, or one
> exact impacted portability contract name without trimming each group by hand?

Rev287 keeps that next step tiny.

## What changed

- `src/micromax/portability_suite.py` now also provides:
  - `select_stdlib_impact_case_names(...)`
  - `refilter_stdlib_impact_groups(...)`
- `selected_boot_stdlib_word_inventory(...)` now accepts:
  - `impact_case_categories`
  - `impact_case_tags`
  - `impact_case_names`
  - `impact_case_name_contains`
- `tools/mxportable.py --stdlib-manifest --show-impact` now also accepts:
  - `--impact-category`
  - `--impact-tag`
  - `--impact-name`
  - `--impact-name-contains`
- human and JSON filter metadata now report those case-level impact filters too.

## Shape

The new case-level filters still do not invent a second replay surface.

Instead, they rebuild the same row-level and combined impact payload from a
filtered subset of the already-selected impact groups:

- `impact_case_names`
- `impact_groups`
- `impact_stages`
- `impact_categories` / `impact_tags`
- exact replay metadata:
  - `retest_name_args`
  - `retest_env`
  - `retest_argv`
  - `retest_json_argv`
  - `retest_command`
  - `retest_json_command`

That means “show me only `errors`” or “show me only `cleanup-error-wins`” stays
honest: the grouped provenance, staged replay plan, and exact rerun commands all
speak about the same reduced portability contract slice.

## Examples

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-name-contains cleanup-error-wins --json
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word try --show-impact --impact-word recover --impact-tag errors
```

Human output can now say things like:

```text
impact filters: tags=errors

[ok] ensure: stdlib-ensure-success-runs-cleanup, ...
      impact cases: stdlib-ensure-failure-reraises-after-cleanup, ...
      impact groups:
        ensure <= ensure :: stdlib-ensure-failure-reraises-after-cleanup, ...
        finally <= ensure -> finally :: stdlib-finally-failure-reraises-after-cleanup, ...
```

Or, for a case-name slice:

```text
impact filters: name-contains=cleanup-error-wins

[ok] ensure: stdlib-ensure-success-runs-cleanup, ...
      impact cases: stdlib-ensure-cleanup-error-wins-on-success, ...
```

## Why this helps

The recent portability/tooling thread now forms a slightly more complete handoff
ladder:

1. manifest coverage,
2. source inventory,
3. dependency inventory,
4. closure inventory,
5. reverse-user inventory,
6. impact inventory,
7. exact combined retest commands,
8. grouped impact provenance,
9. per-group replay metadata,
10. staged replay plans,
11. impacted-word / depth slice filters,
12. impacted portability case filters.

So a future host or future LLM can now move from “this word changed” to either a
full replay plan, one impacted word/stage, or one exact semantic portability
slice like `errors` or `cleanup-error-wins` without hand-editing case lists.
