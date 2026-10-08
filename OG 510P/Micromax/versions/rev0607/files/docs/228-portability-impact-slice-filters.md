# Rev286: filter selected boot-stdlib impact slices by impacted word or depth

Rev285 made selected change impact executable as a staged replay plan, but it
still left one tiny manual step for humans and future LLMs.

`--show-impact` could already answer:

- which impacted boot-stdlib words are downstream of a selected word,
- which exact portability cases belong to each impacted word,
- what shortest stdlib paths explain that impact,
- what exact replay command reruns each group and the combined slice, and
- what root-first shortest-path stages make up the replay plan.

The missing next question was:

> can I ask for only the root stage, only depth 1, or only the `finally` slice?

Rev286 keeps that next step tiny.

## What changed

- `src/micromax/portability_suite.py` now also provides:
  - `select_stdlib_impact_groups(...)`
  - `stdlib_impact_slice(...)`
- `selected_boot_stdlib_word_inventory(...)` now accepts:
  - `impact_filter_words`
  - `impact_word_contains`
  - `impact_distances`
- `tools/mxportable.py --stdlib-manifest --show-impact` now also accepts:
  - `--impact-word`
  - `--impact-word-contains`
  - `--impact-distance`
- JSON filter metadata and human output now both show the active impact filter.

## Shape

The new filters do not invent a second replay surface.

Instead, they rebuild the *same* impact payload from a filtered subset of the
existing impact groups:

- `impact_words`
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

That means “show me only depth 0” or “show me only `finally`” stays honest: the
combined summary, grouped provenance, staged replay plan, and exact rerun
command all describe the same trimmed slice.

## Examples

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word keep --show-impact --impact-distance 0
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word finally --json
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word keep --word ensure --show-impact --impact-distance 1
```

Human output can now say things like:

```text
impact filters: distances=0

[ok] keep: stdlib-keep
      impact words: keep
      impact stages:
        depth 0: keep :: stdlib-keep
          retest: PYTHONPATH=src python tools/mxportable.py --name stdlib-keep
```

Or, for a named impacted slice:

```text
impact filters: words=finally

[ok] ensure: stdlib-ensure-success-runs-cleanup, ...
      impact words: finally
      impact groups:
        finally <= ensure -> finally :: stdlib-finally-success-runs-cleanup, ...
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
11. filterable impact slices.

So a future host or future LLM can now move from “this word changed” to either a
full replay plan or one exact root/depth/word slice without manually trimming a
larger payload first.
