# Rev0895 timely full-suite release runway

Rev0895 keeps the project Python-first and adds a release-evidence lane that can
finish inside short cloudtainer/tooltimer slices. The old aggregate `mxtest`
path is still available for node-level chunk evidence, but whole-suite pytest
collection can exceed the interactive window. `tools/mxrelease.py` therefore
uses a selected-file/node-batch release strategy: discover `tests/test*.py`, run selected batches in fresh pytest children, checkpoint after every batch, split timed-out multi-file batches or slow single files into pytest-node retries, and verify the completed
manifest against the current source attestation.

## What changed

- Added `tools/mxrelease.py` for resumable selected-file/node-batch full-suite evidence with slow-batch and slow-file node splitting.
- Added `make release-suite`, `make release-verify`, and `make release-summary`.
- Added `.artifacts/mxrelease-full-suite.json` as the default full-suite release
  manifest path.
- Extended audit/context/Makefile tests so the release runway is part of the
  handoff contract, not just a loose script.
- Kept `make timely` as a short handoff-health lane and kept `make timely-tests`
  as an optional tiny `mxtest` checkpoint.

## Intended commands

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make timely
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make release-suite
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make release-suite
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make release-verify
```

`make release-suite` returns success for a clean partial checkpoint so humans and
LLMs can call it repeatedly without treating a budget stop as a failure. The
release claim is made only by `make release-verify`, which requires the manifest
to be complete, all files passed, and the embedded source digest to match the
current tree.

## Evidence semantics

A completed rev0895 release manifest is full-suite file evidence, not a
monolithic single-process pytest claim. It is deliberately stricter about
batch-level cleanup: every test file runs in a fresh interpreter with host pytest
plugin autoloading disabled. The manifest records each selected file batch, return code,
elapsed time, parsed pytest counters, a bounded diagnostic tail, environment
metadata, and the source manifest digest borrowed from `mxtest`.

If the source digest changes, the release lane starts fresh instead of carrying
stale passed rows forward. That keeps archive handoffs honest even when docs or
tooling change late in a session.

## Residual risks

- This is still Python reference evidence, not C++ or process-isolation work.
- Per-file isolated evidence does not prove there is no hidden ordering
  dependency in a monolithic pytest process. It is the practical release lane for
  this cloudtainer constraint.
- Dependency lock, CI, package inspection, artifact provenance, and
  archive-versus-package version policy are still separate release-engineering
  work.
