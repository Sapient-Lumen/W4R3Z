# GlassTTY rev0035 validation summary

- revision: rev0035
- extension version: 0.1.12

## Passed here

- `npm --prefix extension run typecheck` → `validation/latest/typecheck-rev0035.txt`
- `npm --prefix extension run build` → `validation/latest/build-rev0035.txt`
- `PYTHONPATH=daemon/src pytest tests/test_cli.py tests/test_native_host.py tests/test_e2e_fixturelab.py tests/test_validate_release.py` → `validation/latest/test-focus-rev0035.txt`
- `PYTHONPATH=daemon/src python -m py_compile daemon/src/glassttyd/cli.py daemon/src/glassttyd/native_host.py` → `validation/latest/py_compile-rev0035.txt`

## Manual browser evidence

- `validation/latest/manual-rev0035-offscreen-fixture-note.json` preserves the honest limit for this revision: no fresh live Chromium+extension session was available here to prove the new offscreen fixture round-trip.

## What rev0035 adds

- base-URL-aware `bridge.offscreen_dom` summaries with link and form samples
- `bridge.offscreen_fixture` and `glassttyd offscreen-fixture` for turning saved HTML into a generic fixture-like capture through the hidden offscreen document
- candidate hints and HTML samples that can later be compared against visible-tab fixture captures before hard-coding adapter logic
