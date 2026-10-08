# Rev0896 — communicative testing runway

The rev0895 release lane proved the full suite can be accumulated in short
Python-only selected-file/node batches. Rev0896 makes that facility easier for
weaker handoff agents to operate and refactor.

## What changed

- Added `tools/mxtoolrun.py` as the shared child-process, timeout teardown,
  captured-output, heartbeat, duration-formatting, and deterministic-environment
  helper used by `mxtimely` and `mxrelease`.
- `mxtimely` now writes a v2 summary with total elapsed time and the slowest
  step, while preserving the compact human summary.
- `mxrelease` now records per-batch timeout seconds, command timing rows, an
  aggregate `timing` block, slowest-batch samples, progress lines before each
  batch, and a machine-readable `next_action` block.
- Added `python tools/mxrelease.py --next` and `make release-next` so a future
  session can ask the manifest what to do next without re-reading the runner.
- Added focused tests for the shared runner, timing summaries, and next-action
  guidance.
- `mkrevzip` now carries the compact timely and full-suite release evidence
  manifests instead of dropping them with other transient `.artifacts` files.

## How to use the lane

For a quick health pass:

```bash
make timely
```

For a short full-suite release slice:

```bash
make release-suite
```

For the next handoff action:

```bash
make release-next
```

For the complete/current full-suite release claim:

```bash
make release-verify
```

`make release-suite` may exit cleanly with a partial manifest. That is not a
release claim. A weaker model should read `make release-next` and follow the
reported command: continue if batches remain, inspect the manifest summary if a
batch failed or timed out, and verify only after the manifest is complete and
passed.

## Testing approaches worth keeping

- Keep the Python implementation as the reference oracle.
- Use `make timely` for handoff-health evidence.
- Use `make release-suite` / `make release-verify` for full-suite evidence.
- Use focused pytest files for a narrow revision contract before running the
  release lane.
- Keep source/environment attestations tied to the manifest so stale evidence
  fails closed.
- Keep slowest-batch samples in the manifest; they are the cheapest guide for
  future batch-size or timeout tuning.

## Non-goals

This revision does not change runtime capability or plugin-security semantics.
It only makes the evidence runway more communicative, timed, modular, and easier
to operate inside short cloudtainer windows.
