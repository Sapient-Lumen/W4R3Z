# rev0114 focused validation

## Passed here

- `PYTHONPATH=daemon/src pytest -q tests/test_e2e_fixturelab.py -k 'playwright_extension_launch_plan or launch_playwright_persistent_probe' -q`
  - result: `9 passed`
- `PYTHONPATH=daemon/src pytest -q tests/test_playwright_browsers.py -k 'discover_playwright_browser_install_reports_imported_bundle or playwright_extension_launch_plan_recommends_offline_import' -q`
  - result: `2 passed`
- `npm run typecheck`
- `npm run build`

## What changed

- GlassTTY now prefers Playwright's documented `channel="chromium"` persistent launch when the cached browser matches the current expected Playwright package.
- When the cache name drifts away from the expected package identity, GlassTTY deliberately falls back to explicit `executable_path` launch instead of pretending the channel path is aligned.

- `python scripts/doctor.py --pretty`
  - result: passed

## Honest limits

- A broader combined pytest pass over `tests/test_e2e_fixturelab.py tests/test_playwright_browsers.py` was attempted earlier in this session but the container runtime dropped the process wait channel before returning a trustworthy final summary. This archive does **not** claim that broader pass as green.
- No fresh live browser/native-messaging round-trip is claimed here.
