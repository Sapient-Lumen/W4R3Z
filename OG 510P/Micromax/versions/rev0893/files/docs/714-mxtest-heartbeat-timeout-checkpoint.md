# Rev768 — mxtest heartbeat, chunk timeout, and running checkpoints

## Why this was risky

Rev767 made mxtest safe against a serious selection failure: diagnostic verbosity could no longer erase exact node ids or widen an empty chunk into pytest defaults. While trying to push toward full-suite evidence in this cloudtainer, a different validation-trust gap showed up: a long pytest child can still be externally terminated before a chunk completes. If the aggregate manifest is only written after each finished chunk, a killed first chunk can leave no JSON evidence at all.

That is bad handoff behavior. The whole purpose of mxtest is to make large validation runs auditable even when they are interrupted.

## What changed

`tools/mxtest.py` now has a parent-side child-process heartbeat. The child still inherits stdout/stderr, so ordinary pytest dots and failure output are not captured or rewritten. When a child is quiet for the configured interval, the parent emits a small liveness line such as:

```text
mxtest: still running pytest 205 tests across 17 files (30s elapsed)
```

The default interval is 30 seconds. It can be set with either:

```bash
MXTEST_HEARTBEAT_SECONDS=10 python tools/mxtest.py ...
python tools/mxtest.py --heartbeat 10 ...
```

Use `0` to silence the heartbeat.

`tools/mxtest.py` also now has a non-isolated chunk timeout:

```bash
python tools/mxtest.py --chunk 1/8 --chunk-timeout 180
python tools/mxtest.py --run-chunks 8 --chunk-timeout 180 --json .artifacts/mxtest-all.json
```

The older `--file-timeout` remains the per-file timeout for `--isolate-files`. The new `--chunk-timeout` is for ordinary non-isolated pytest children.

Finally, aggregate `--run-chunks --json` now writes a `running` checkpoint record before starting each non-empty chunk. If the process is killed mid-chunk, the manifest can still say which chunk was active, with `status="partial"` and `complete=false`, instead of leaving no artifact. `--resume` treats that record as not reusable and reruns the chunk.

A same-revision hardening pass also changed `write_json_summary(...)` to write through a same-directory temporary file, flush/fsync it, and promote it with `os.replace(...)`. The goal is boring but important: a checkpoint update should not truncate or half-write the only resume witness when the parent process is interrupted during JSON emission. If replacement fails, the previous manifest is left intact and the temporary file is cleaned up.

## Refactor details

The child execution path moved from `subprocess.run(...)` to a small `run_subprocess_with_heartbeat(...)` loop. The timeout teardown path uses best-effort terminate/kill handling and returns the existing timeout code `124`, so manifest status vocabulary remains stable.

The aggregate manifest code now treats `running`, `partial`, unknown statuses, and missing records as incomplete. A small `aggregate_complete(...)` helper keeps `complete` aligned between manifest writing and verification.

The default doctor lane now includes `tests/test_mxtest.py`, because validation-runner safety should be part of the normal handoff preflight rather than a one-off suite.

## Regression coverage

New tests cover:

- heartbeat interval selection from defaults, environment, and CLI override;
- liveness output from `run_subprocess_with_heartbeat(...)`;
- timeout teardown returning `124`;
- forwarding `--chunk-timeout` to single-chunk and aggregate non-isolated runs;
- recording heartbeat and chunk-timeout settings in plan JSON;
- writing a `running` checkpoint before invoking pytest;
- atomically writing JSON summaries without leaving temp files;
- preserving the previous manifest if `os.replace(...)` fails;
- verifying a manifest with a `running` checkpoint as partial/incomplete, not passed.

## Remaining risk

This still does not prove the full suite is clean. It makes the full-evidence lane more survivable: long chunks are observable, non-isolated chunks can be bounded, and interrupted aggregate runs leave a useful manifest checkpoint.

The next validation step should be a chunked full run using either `--isolate-files` for maximum isolation or `--chunk-timeout` for faster non-isolated chunks. If the platform kills the run, the current manifest should now identify the active chunk instead of disappearing.

## Validation notes

Focused validation in this cloudtainer before packaging:

- `python -m py_compile tools/mxtest.py tools/mxdoctor.py tests/test_mxtest.py tests/test_mxdoctor.py` passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_mxtest.py` passed: 72 tests.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_mxdoctor.py` passed: 9 tests.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPYCACHEPREFIX=/tmp/micromax_pycache python tools/mxtest.py --chunk 1/2 --strategy segment --chunk-timeout 30 --heartbeat 0 --json /mnt/data/micromax_rev0768_mxtest_cli_probe.json --durations 0 -- tests/test_mxtest.py` passed: 36 selected tests.
- `bash scripts/lint.sh` passed after the code changes.
