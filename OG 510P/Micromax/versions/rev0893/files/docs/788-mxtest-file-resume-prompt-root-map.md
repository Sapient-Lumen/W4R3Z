# Rev829 — mxtest file resume and prompt root row map

## Intent

Rev829 targets the highest-risk unfinished lane from the recent handoffs: full-suite evidence in a cloudtainer that can interrupt long runs. Rev824 made isolated-file progress checkpointable, but `--resume` still skipped only whole passed chunks. A partial chunk could preserve dozens of passed file rows and then rerun them all on the next attempt.

## Changes

- `tools/mxtest.py` now records `nodeids_digest` for each isolated file row.
- `--run-chunks --isolate-files --resume` can reuse passed file rows inside a matching partial chunk.
- File-level resume is gated by matching source digest, environment digest, chunk selection digest, file name, selected count, status, return code, and per-file node-id digest when present.
- Manifest summaries now surface resumed-file counts and flag resumed/skipped file rows.
- `prompt_suggestions.py` now uses a table-driven root-command prompt-row map for specialized root command previews instead of a long inline `if/elif` ladder.

## Audit correction

The wasteful behavior was not the checkpointing itself; the waste was that the checkpoint was not actionable on resume. Rev829 turns partial manifests into useful restart evidence, so a cloudtainer interruption during a large isolated chunk does not force already-passed files in that chunk to rerun.

## Validation

Focused lanes run during the rev829 handoff:

```bash
python tools/mxlint.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q tests/test_mxtest.py --durations=10
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q tests/test_editor_prompt_completion_hostcalls.py tests/test_prompt_completion.py tests/test_prompt_rows.py tests/test_prompt_rank.py --durations=10
```

A final context/revision/package smoke should still run before packaging.

## Remaining risk

Full aggregate suite evidence is still pending. The recommended command is now more useful after interruption:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --run-chunks 8 \
  --strategy segment \
  --isolate-files \
  --resume \
  --json .artifacts/mxtest-all.json \
  --durations 0
```
