# Rev0830 — mxtest file budget and dispatcher seam audit

Rev0830 continues the evidence-lane work from rev0829.  The goal was to make a full-suite manifest more achievable inside a cloudtainer that can interrupt long commands, without turning the handoff into more process bureaucracy.

## What changed

- Added `tools/mxtest.py --max-new-files N` for `--run-chunks --isolate-files`.
- Budgeted isolated runs now execute at most `N` non-resumed files, then record remaining selected files as explicit `not_run` file rows with `nodeids_digest` evidence and `skip_reason=max-new-files-reached`.
- Partial chunks with passed, resumed, and budget-skipped file rows keep their file rows in selected-file order.
- Manifest summaries now surface `skipped_files=N` for budgeted chunks.
- `--verify-current` now treats structurally valid partial manifests as resume-safe when source and environment digests still match.  A partial manifest is not a full-suite pass, but it is valid restart evidence.

## Audit finding and correction

A bounded 32-chunk aggregate attempt found a real refactor seam regression from the command-family extraction: `tests/test_editor_script_context_fs_caps.py` still monkeypatched `micromax_editor.command_dispatcher.checked_sandbox_path` to prove the scripted `open` command rechecks symlink containment after a late parent swap.  After `open` moved to `buffer_commands.py`, that monkeypatch no longer reached the command handler.

Rev0830 keeps the extracted command family but restores the compatibility seam:

- `command_dispatcher.py` re-exports `checked_sandbox_path`.
- `buffer_commands.c_open` resolves that checker through `micromax_editor.command_dispatcher` at call time for the scripted-open path.

This keeps the late-symlink recheck probe meaningful and avoids weakening the filesystem capability boundary.

## Evidence from this turn

A direct 8-chunk attempt was still too coarse: the first selected file contained 258 prompt-completion tests and the cloudtainer interrupted it before completion.  A 32-chunk plan reduced chunk size to about 67-68 selected tests.

The bounded aggregate smoke then ran:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --run-chunks 32 \
  --strategy segment \
  --isolate-files \
  --resume \
  --max-new-files 3 \
  --file-timeout 180 \
  --json .artifacts/mxtest-all-32-rev0830.json \
  --durations 0 \
  --summary-limit 8
```

It collected 2,154 tests and made bounded progress: two chunks passed, one chunk became partial after one small file passed and two files were budget-skipped, and the remaining chunks were recorded as `not_run` with file-level skip rows.  This is not a full-suite pass.  It is useful restart evidence and it also found the dispatcher compatibility bug above.

## Recommended next command

Continue the same manifest, not the old 8-chunk command:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --run-chunks 32 \
  --strategy segment \
  --isolate-files \
  --resume \
  --max-new-files 8 \
  --file-timeout 180 \
  --json .artifacts/mxtest-all-32.json \
  --durations 0
```

Raise or lower `--max-new-files` based on the available command window.  Use `--verify-current` on partial manifests to confirm they are still safe to resume after source/environment drift checks.
