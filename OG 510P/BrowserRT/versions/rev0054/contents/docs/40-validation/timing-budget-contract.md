# Timing budget contract

Revision: rev0028.

The cloudtainer can run tests, but timing windows are precious and process
persistence across turns is not guaranteed. The test facility therefore records
timing as evidence and as future scheduling input.

## Rules

- Every manifest task has `estimatedMs` and `timeoutMs`.
- The runner records actual `durationMs` per task.
- Reports include slowest tasks and estimate misses.
- `--history` updates a bounded timing-history artifact.
- Sharding currently uses manifest estimates; future revisions may use timing
  history once enough samples exist.
- A task exceeding 2x estimate should either be optimized, split, or have its
  estimate updated with a reason.

## Current artifacts

- `artifacts/validation/REV0044-TEST-HARNESS-RUN.json`.
- `artifacts/validation/REV0044-TEST-TIMING-HISTORY.json`.
- `artifacts/validation/REV0044-TEST-HARNESS-RUN.json`.
- `artifacts/validation/REV0044-TURN-BOOTSTRAP-RUN.json`.
- `artifacts/validation/REV0044-TURN-SMOKE-RUN.json`.

## Non-claim

Cloudtainer timing is useful for regression detection inside this environment. It
is not evidence of real user-device performance.
