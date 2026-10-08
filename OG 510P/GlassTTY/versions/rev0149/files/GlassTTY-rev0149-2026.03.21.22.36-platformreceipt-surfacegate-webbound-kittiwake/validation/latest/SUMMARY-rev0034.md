# GlassTTY rev0034 validation summary

- revision: rev0034
- extension version: 0.1.11

## Passed here

- `npm --prefix extension run typecheck` → `validation/latest/typecheck-rev0034.txt`
- `npm --prefix extension run build` → `validation/latest/build-rev0034.txt`
- `PYTHONPATH=daemon/src pytest -q tests/test_cli.py tests/test_native_host.py tests/test_e2e_fixturelab.py tests/test_validate_release.py` → `validation/latest/test-focus-rev0034.txt`
- `PYTHONPATH=daemon/src python -m py_compile daemon/src/glassttyd/cli.py daemon/src/glassttyd/native_host.py scripts/e2e-fixturelab.py` → `validation/latest/pycompile-rev0034.txt`

## Manual browser evidence

- `validation/latest/manual-rev0034-offscreen-dom-note.json` preserves the honest limit for this revision: no fresh live Chromium+extension session was available here to prove the new offscreen DOM round-trip.

## What rev0034 adds

- active offscreen ping/ready reporting instead of only a one-shot offscreen startup signal
- `bridge.offscreen_dom` and `glassttyd offscreen-dom` for parsing saved HTML through a hidden browser-native DOM context
- selector counts, heading samples, and editable-candidate hints from that hidden DOM summary
