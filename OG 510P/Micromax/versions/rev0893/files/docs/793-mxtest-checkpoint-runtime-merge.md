# Rev0834: mxtest checkpoint/runtime merge

Rev0834 fixes a lineage fork in the rev0833 handoff archives and keeps the test-evidence lane moving forward.

Two rev0833 archives existed with different content. The earlier rev0833 bronze archive added per-test pytest checkpoints via `--checkpoint-tests`; the later rev0833 silver archive added runtime-budget stopping via `--max-runtime-seconds`, but the bronze per-test checkpoint files were no longer present. Rev0834 merges both lines forward under a new revision number.

## What changed

- Restored `tools/mxtest_progress_plugin.py`, the small pytest child plugin that writes JSONL records after resume-safe per-test terminal points.
- Restored `tools/mxtest.py --checkpoint-tests` for isolated runs.
- Preserved the rev0833 silver runtime-budget behavior: `--max-runtime-seconds` still stops deliberately, caps child timeouts by remaining runtime, and records remaining chunks/spans as `not_run`.
- Merged the two behaviors: runtime-bounded isolated runs can now use larger per-file pytest subprocesses with per-test progress instead of paying many small batch-startup costs.
- Hardened signal interruption: when `run-chunks` catches `SIGTERM`/`SIGINT` during a chunk, the interrupted chunk is preserved, remaining planned chunks are marked `not_run` with `skip_reason=interrupted-SIGNAL`, and the process signal return code is kept as `process_returncode`.
- Cleaned manifest summaries so a whole resumed chunk is shown as `resumed` rather than `resumed skipped`.
- Extended per-test checkpoints to child timeout rows: when a checkpointed pytest child returns timeout code `124`, completed prefix tests can be recorded as passed and only the unfinished suffix is marked `timed_out`.

## Evidence lane

The default Makefile path now combines the two rev0833 lines:

```bash
make test-all-chunks
```

which expands to the 64-chunk isolated/resume lane with:

```bash
--checkpoint-tests \
--max-new-tests "$MAX_NEW_TESTS" \
--max-new-files "$MAX_NEW_FILES" \
--test-batch-size "$TEST_BATCH_SIZE" \
--file-timeout "$FILE_TIMEOUT" \
--max-runtime-seconds "$MAX_RUNTIME_SECONDS"
```

`TEST_BATCH_SIZE` now defaults to `0`. That means one pytest subprocess per selected file/span; `--checkpoint-tests` is the default restart-safety mechanism. Use a positive `TEST_BATCH_SIZE` only for files that need smaller process-level isolation.

## Audit result

A bounded aggregate pass before this merge showed that the latest silver archive had no `--checkpoint-tests` option or `tools/mxtest_progress_plugin.py`, even though an earlier rev0833 archive had claimed them. This was a real archive-lineage regression rather than a cosmetic docs issue.

A second aggregate smoke after the merge used `--checkpoint-tests`, `--max-runtime-seconds`, and `--resume` together. It collected the suite, ran the first two 34-test chunks and part of the third chunk, then verified the partial manifest as source/environment-current and resume-safe.

## Remaining risk

Rev0834 still does not claim a complete aggregate suite pass. It restores and combines the restart mechanisms needed to get there without depending on one uninterrupted cloudtainer window.
