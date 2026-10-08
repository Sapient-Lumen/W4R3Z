# Rev0894 cloudtainer timely tool runway

Rev0894 is a tooling-only landing.  It keeps the project Python-first and makes
the normal handoff checks fit short cloudtainer/tooltimer windows without
switching the test strategy to C++.

## What changed

- Added `tools/mxtimely.py`, a bounded wrapper for the everyday evidence lane.
- Added `make timely` for the compact default lane: context, audit, lint,
  portability, and the fast doctor preflight.
- Added `make timely-tests` for an optional tiny resumable `mxtest` checkpoint
  slice; it intentionally skips doctor so the short test lane does not stack two
  pytest orchestrators.
- Added quiet portability output for `tools/mxportable.py --quiet`.
- Shortened `mxdoctor` defaults so the default doctor lane exercises selected
  risk seams rather than a broad authority-file sweep.
- Kept the full/resumable lanes available through `make test-all-chunks`,
  `make doctor-full`, and `make doctor-chunked`.

## Non-goals

This revision does not claim full-suite release evidence.  A successful timely
run means the repo handoff tools are healthy in a constrained container.  A
public release still needs a fresh completed aggregate manifest, dependency lock,
CI/package inspection, archive hashes, and provenance notes.

## Recommended short-window commands

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make timely
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make timely-tests
python tools/mxcontext.py --check
python tools/mxaudit.py --check
python tools/mxlint.py
python tools/mxportable.py --quiet
```

The optional test lane writes `.artifacts/mxtimely-mxtest.json`.  A nonzero
`mxtest` exit is acceptable to `mxtimely` only when the manifest is a clean
budget-limited partial checkpoint with passed progress and no failed, timed-out,
running, or partial test rows.

## Why not C++ now

The remaining risk is not Python test weakness.  It is repeatable evidence,
resource budgets, lifecycle contracts, and release hygiene.  Python stays the
reference oracle.  C++ remains useful later as a small differential or hostile
host-boundary probe, not as the main test rewrite.
