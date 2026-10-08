# rev0026 validation summary

## Passed

- `pytest -q tests/test_e2e_fixturelab.py -k 'not fixturelab_e2e_smoke'`
- `pytest -q tests/test_browser_binaries.py tests/test_dev_tools.py tests/test_validate_release.py tests/test_native_host.py`
- `npm run typecheck`
- `npm run build`
- `python scripts/doctor.py --pretty`
- `GLASSTTY_PLAYWRIGHT_ALLOW_SYSTEM_EXECUTABLE=1 python scripts/doctor.py --pretty`
- `python scripts/chrome-for-testing.py inspect --pretty`
- `python -m playwright install --help`

## Important local fact surfaced by rev0026

In this container, Playwright is installed but no bundled Chromium cache is present, so GlassTTY now skips the Playwright persistent extension lane by default with `skip_reason=missing-bundled-chromium`. The old system-browser behavior still exists, but only as an explicit risky override.

## Not newly proven here

- no successful bundled-Chromium Playwright persistent browser proof was captured in this container
- no successful native-host/socket round-trip was captured in this container
- a fresh `scripts/e2e-fixturelab.py` attempt still did not leave behind a stable JSON report artifact in this environment
