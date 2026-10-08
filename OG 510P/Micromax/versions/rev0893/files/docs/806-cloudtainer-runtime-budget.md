# Rev848 — cloudtainer-safe aggregate runtime budget

Rev848 corrects a cloudtainer-specific waste pattern in the full-suite evidence lane. The archive already had resumable `mxtest` checkpoints, but the default aggregate commands still asked for long or unbounded children:

- `make test-all-chunks` defaulted `MAX_RUNTIME_SECONDS` to 240 seconds;
- `mxdoctor --chunked` emitted no `--max-runtime-seconds` unless the caller supplied one.

In this cloudtainer, long children are externally interrupted around the session/tool boundary. `mxtest` can preserve those interruptions, but relying on outside SIGTERM is noisier than stopping gracefully at a known checkpoint boundary.

Rev848 makes the default aggregate lane short and deliberate:

- `Makefile` now defaults `MAX_RUNTIME_SECONDS ?= 25`;
- `mxdoctor --chunked` now includes a 25-second `--max-runtime-seconds` by default;
- local long-run users can still override `MAX_RUNTIME_SECONDS`, pass `--max-runtime-seconds 0`, or set `MXDOCTOR_CHUNKED_MAX_RUNTIME_SECONDS`.

The point is not to make the suite smaller. It is to make each resume invocation finish on its own terms, checkpoint the manifest, and return control to the handoff loop before the cloudtainer has to kill it.

## Budget timeout audit

The first rev848 aggregate rebuild exposed a second waste bug. With a 25-second aggregate budget, mxtest could start a new pytest child with only a few seconds left, kill it when the runtime budget expired, and then record that planned budget stop as a real `timed_out` test-file failure. Rev848 now distinguishes a runtime-budget-derived child timeout from a configured file timeout: any completed per-test prefix is preserved as passed, and the remaining selected tests are written as `not_run` with `max-runtime-seconds-reached`.

A related preservation issue also surfaced: chunk-level skip reasons can combine file-budget and runtime-budget reasons, for example `max-runtime-seconds-reached+max-new-files-reached`. Tail preservation now treats such combined reasons as resumable when every component is an intentional bounded stop, so later matching passed chunks are not erased just because two budget guards fired in one checkpoint.
