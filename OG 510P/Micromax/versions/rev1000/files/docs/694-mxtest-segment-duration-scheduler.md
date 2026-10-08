# mxtest segment and duration scheduler (rev750)

Rev750 tightens the chunked test runway that rev748 and rev749 introduced.  The previous runner could prove exactly which node ids were selected, but its only scheduler was a contiguous node-count slice.  That made handoff validation brittle: one slice could accidentally inherit a docs-navigation or prompt-completion cliff even when every chunk had the same number of node ids.

## New strategies

`tools/mxtest.py` now accepts `--strategy`:

```bash
python tools/mxtest.py --plan --chunks 8 --strategy node
python tools/mxtest.py --plan --chunks 8 --strategy file
python tools/mxtest.py --plan --chunks 8 --strategy segment
python tools/mxtest.py --plan --chunks 8 --strategy duration --history .artifacts/mxtest-chunk-1.json
```

The strategies mean:

- `node`: the rev748/rev749 behavior, a deterministic contiguous node-id slice.
- `file`: keep test files whole and schedule files by test count.
- `segment`: keep ordinary files whole, but split oversized files into contiguous segments before scheduling.
- `duration`: keep files whole and schedule them by the largest per-file duration observed in previous isolated mxtest JSON summaries; files with no history fall back to test count.

`make test-plan` and `make test-chunk CHUNK=...` now use `--strategy segment`.  This is the best cold-start default because it does not require historical JSON, but it also avoids letting one very large file own a chunk.

## History input

When a run uses `--isolate-files --json`, the JSON summary contains a `files` list with per-file durations and statuses.  Rev750 can read one or more of those files through `--history`.  If the same file appears in multiple histories, mxtest keeps the largest duration so a slow but real run is not hidden by a later warm-cache run.

The plan records:

- `strategy`
- `strategy_weight`
- `strategy_weight_unit`
- `history_paths`
- `history_file_count`
- per-chunk strategy metadata
- copyable commands that preserve strategy, history paths, and pytest args after `--`
- `execution_pytest_args` plus `dropped_pytest_selectors`, so positional collection selectors cannot widen an explicit-node chunk run

## Trust boundary

The important property is not that the scheduler is perfect.  It is that the scheduler is explicit.  A future handoff can now say:

```text
collected: 1485
strategy: segment
chunks: 1:186 2:186 3:186 4:186 5:186 6:185 7:185 8:185
```

or:

```text
strategy: duration
history_file_count: 137
```

and the JSON manifest explains how that selection was made.  It also records which pytest args were used for collection and which positional selectors were dropped during execution after exact node ids were selected.  That keeps full-suite evidence from becoming a vague statement like "the tests are too slow here".

## Remaining risk

`duration` still uses file-level history, not per-node historical timing.  If a single file has one very slow test and many fast tests, the scheduler can only distribute that cost when `segment` is used or when the file itself is split by future per-node history.  A later revision can add per-node duration ingestion without changing the main mxtest contract.
