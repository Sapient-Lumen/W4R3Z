# rev0027 validation summary

## Passing checks

- `python -m py_compile scripts/playwright_browsers.py scripts/playwright-browsers.py scripts/chrome-for-testing.py scripts/doctor.py scripts/e2e-fixturelab.py tests/test_playwright_browsers.py tests/test_e2e_fixturelab.py`
- `pytest -q tests/test_playwright_browsers.py tests/test_e2e_fixturelab.py` → `25 passed, 1 skipped`
- `pytest -q tests/test_validate_release.py` → `2 passed`
- `pytest -q tests/test_native_host.py` → `2 passed`
- `pytest -q tests/test_dev_tools.py::test_doctor_script_reports_manifest_and_wrapper tests/test_dev_tools.py::test_cli_doctor_command_runs_with_pythonpath` → `2 passed`
- `npm --prefix extension run typecheck`
- `npm --prefix extension run build`
- `python scripts/doctor.py --pretty`

## New proof artifacts

- `validation/latest/playwright-import-archive-rev0027.json`
- `validation/latest/playwright-inspect-rev0027.json`
- `validation/latest/doctor-offline-seeded-rev0027.json`
- `validation/latest/chrome-for-testing-offline-install-rev0027.json`

## Honest limits

- rev0027 proves offline browser-cache seeding and launch-plan changes, not a live browser/native-host round-trip
- no fresh real-browser Playwright persistent run was claimed in this container
