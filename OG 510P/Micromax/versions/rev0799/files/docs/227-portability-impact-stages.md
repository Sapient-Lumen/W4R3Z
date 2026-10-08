# Rev285: expose staged replay plans for selected boot-stdlib impact slices

Rev284 made selected change impact executable at the per-group level, but it
still left one tiny planning step for humans and future LLMs.

`--show-impact` could already answer:

- which impacted boot-stdlib words are downstream of a selected word,
- which exact portability cases belong to each impacted word,
- what shortest stdlib paths explain that impact, and
- what exact replay command reruns either the full slice or one impacted group.

The missing next question was:

> what is the smallest sensible order to replay those exact groups?

Rev285 keeps that next step tiny.

## What changed

- `src/micromax/portability_suite.py` now also provides:
  - `stdlib_impact_distance(...)`
  - `stdlib_impact_stages(...)`
- each `impact_groups` row now also carries:
  - `distance`
- each selected word plus the combined selected `impact_summary` now also carry:
  - `impact_stages`
  - `impact_stage_count`
- `tools/mxportable.py --stdlib-manifest --show-impact`
  - human mode now prints a tiny `impact stages:` section
  - JSON mode carries the same staged replay payload machine-readably

## Shape

Each `impact_stages` row names one shortest-path depth and carries:

- `distance`
- `words`
- `word_count`
- `selected_words`
- `selected_word_count`
- `case_names`
- `case_count`
- the same exact replay metadata already used elsewhere:
  - `retest_name_args`
  - `retest_env`
  - `retest_argv`
  - `retest_json_argv`
  - `retest_command`
  - `retest_json_command`
- optional joined `impact_categories` / `impact_tags`

That keeps the payload tiny while giving future hosts, scripts, and LLMs one
honest answer to “what should I replay first?” without pretending Micromax now
has a richer scheduler.

## Example

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word keep --show-impact
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word keep --word ensure --show-impact --json
```

Human output now includes staged lines like:

```text
impact stages:
  depth 0: keep, ensure :: stdlib-keep, stdlib-ensure-success-runs-cleanup, ...
    retest: PYTHONPATH=src python tools/mxportable.py --name stdlib-keep ...
  depth 1: bi, tri, finally :: stdlib-bi, stdlib-tri, stdlib-finally-success-runs-cleanup, ...
    retest: PYTHONPATH=src python tools/mxportable.py --name stdlib-bi ...
```

And merged selections can collapse a downstream word back to `depth 0` when it
was also selected directly, for example `finally` in an `ensure + finally`
selection.

## Why this helps

The recent portability thread now forms a small but fairly complete handoff
ladder:

1. manifest coverage,
2. source inventory,
3. dependency inventory,
4. closure inventory,
5. reverse-user inventory,
6. impact inventory,
7. exact combined retest commands,
8. grouped impact provenance,
9. grouped structured replay metadata,
10. staged replay plans.

So a future host or future LLM can now move from “this word changed” to either
one exact group replay command or a tiny root-first replay order without
inventing an ordering policy by hand.
