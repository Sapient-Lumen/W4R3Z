# Resumable mxtest manifest (rev749)

Rev751 extends this manifest from per-chunk evidence to all-chunk evidence: `--run-chunks N` writes one aggregate JSON file, `--resume` skips only previously passed chunks whose ordered `nodeids_digest` still matches the current collection, and `make test-all-chunks` provides the default segment-scheduled handoff path.  See `docs/695-mxtest-all-chunks-resume.md`.


Rev748 introduced `tools/mxtest.py` so large handoff archives could run pytest in deterministic chunks.  Rev749 tightens that runway: the JSON plan now records enough metadata to resume and audit chunks, and command-line pytest filters are forwarded consistently to both collection and execution.

## What changed

`python tools/mxtest.py --plan --chunks 8 --json .artifacts/mxtest-plan.json` now includes:

- `first` / `last` selected node ids
- `file_count` for the current selection
- legacy `chunks` count list
- `chunk_plan`, with one entry per chunk
- a ready-to-copy chunk command for each chunk

Each run JSON now includes a stable `status` string:

```text
passed | failed | timed_out
```

Per-file isolated records also include the same status, so a timeout is not just a nonzero return code hidden in text output.

## Extra pytest args

Rev748 accepted extra pytest args after `--`, but the run path only used them during collection.  Rev749 forwarded extra args into the actual pytest subprocesses as well, including isolated file runs.  Rev750 tightens that contract for explicit-node execution: positional selectors such as `tests/foo.py` are used during collection, then recorded as `dropped_pytest_selectors` rather than passed back into pytest where they could widen a chunk after exact node ids were selected.  Option args such as `-k smoke` remain in `execution_pytest_args`:

```bash
python tools/mxtest.py --chunk 1/8 -- -k replace
python tools/mxtest.py --isolate-files -- -k smoke
```

That keeps filtered collection and filtered execution aligned.

## Remaining risk

The runner is still deliberately small, but rev750 adds explicit `node`, `file`, `segment`, and `duration` strategies.  `segment` is now the Makefile default for cold-start chunking, while `duration` can consume previous isolated-run JSON summaries.  The remaining gap is per-node historical timing inside a single very slow file; see `docs/694-mxtest-segment-duration-scheduler.md`.

## Archive hygiene

Rev749 also treats `.artifacts/` as transient output for both `mkrevzip` and `mxpack`.  Local mxtest JSON summaries are useful evidence while working, but release archives should carry the source/docs/tests that reproduce them, not stale run output from one machine.
