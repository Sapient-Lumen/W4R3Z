# Rev284: expose exact per-impact-word replay metadata for selected boot-stdlib slices

Rev283 made selected change impact explainable, but it still left one tiny
operational gap for humans and future LLMs.

`--show-impact` could already answer:

- which impacted boot-stdlib words are downstream of a selected word,
- which exact portability cases belong to each impacted word,
- what shortest stdlib paths explain that impact,
- what combined categories/tags describe the whole slice, and
- what one combined replay command reruns the full impacted slice.

The missing last mile was *structured per-group replay*.

A user could now see that `finally` contributes four cleanup cases, but still had
one more manual step if they wanted to:

> rerun only the `finally` slice,
>
> hand those exact args to a subprocess without shell parsing, or
>
> let a future LLM/script choose between shell text and structured argv/env.

Rev284 keeps that next step tiny.

## What changed

- `src/micromax/portability_suite.py` now also provides:
  - `portability_retest_env(...)`
  - `portability_retest_argv(...)`
  - `portability_retest_metadata(...)`
- each `impact_groups` row now also carries:
  - `retest_name_args`
  - `retest_env`
  - `retest_argv`
  - `retest_json_argv`
  - `retest_command`
  - `retest_json_command`
- the combined selected `impact_summary` now carries the same structured replay
  fields, not just shell command strings
- `tools/mxportable.py --stdlib-manifest --show-impact`
  - human mode now prints a tiny per-group `retest:` line
  - JSON mode carries the same structured replay payload machine-readably

## Shape

Each impacted group can now be used in two ways:

1. shell/copy-paste replay via `retest_command` / `retest_json_command`
2. structured replay via `retest_env`, `retest_argv`, and `retest_json_argv`

That keeps the surface tiny while being friendlier to subprocess wrappers,
future ports, and future LLM handoff.

## Example

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word keep --word ensure --show-impact
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --json
```

Human output now includes grouped replay lines like:

```text
impact groups:
  bi <= keep -> bi :: stdlib-bi
    retest: PYTHONPATH=src python tools/mxportable.py --name stdlib-bi
  finally <= ensure -> finally :: stdlib-finally-success-runs-cleanup, ...
    retest: PYTHONPATH=src python tools/mxportable.py --name stdlib-finally-success-runs-cleanup ...
```

And JSON now exposes the same group in a shell-free form too:

```json
{
  "word": "finally",
  "retest_env": {"PYTHONPATH": "src"},
  "retest_argv": [
    "python",
    "tools/mxportable.py",
    "--name",
    "stdlib-finally-success-runs-cleanup"
  ]
}
```

## Why this helps

The recent portability thread now forms a more complete tiny ladder:

1. manifest coverage,
2. source inventory,
3. dependency inventory,
4. closure inventory,
5. reverse-user inventory,
6. impact inventory,
7. exact combined retest commands,
8. grouped impact provenance,
9. grouped structured replay metadata.

So a future host or future LLM can now move from “this word changed” to either
“rerun the whole affected slice” or “rerun just the `finally`-caused part”
without reconstructing shell arguments by hand.
