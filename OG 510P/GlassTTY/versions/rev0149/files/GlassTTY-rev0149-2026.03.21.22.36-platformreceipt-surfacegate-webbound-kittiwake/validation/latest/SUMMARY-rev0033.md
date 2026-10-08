# GlassTTY rev0033 validation summary

- revision: rev0033
- extension version: 0.1.10

## Passed here

- `npm --prefix extension run typecheck` → `validation/latest/typecheck-rev0033.txt`
- `npm --prefix extension run build` → `validation/latest/build-rev0033.txt`
- `pytest -q tests/test_cli.py tests/test_e2e_fixturelab.py tests/test_cdp_inspect.py tests/test_validate_release.py` → `validation/latest/test-focus-rev0033.txt`
- `pytest -q tests/test_dev_tools.py -k contexts_parser` → `validation/latest/test-dev-tools-contexts-rev0033.txt`
- `python scripts/doctor.py --pretty` → `validation/latest/doctor-rev0033.json`
- `python -m py_compile scripts/e2e-fixturelab.py daemon/src/glassttyd/cli.py scripts/doctor.py` → `validation/latest/py-compile-rev0033.txt`

## Manual browser evidence

- `validation/latest/manual-rev0033-offscreen-probe-attempts.json` preserves three honest raw-Chromium launch attempts for the new offscreen probe lane.
- In this container, all three attempts failed before DevTools target listing stabilized, so rev0033 does **not** claim a live offscreen probe proof.

## What rev0033 adds

- optional hidden offscreen diagnostics document creation via `bridge.probe` / `bridge.contexts` and matching CLI flags
- new bundled offscreen extension page and background handshake
- offscreen-aware `runtime.getContexts()` summarization in the e2e helper and probe lane
