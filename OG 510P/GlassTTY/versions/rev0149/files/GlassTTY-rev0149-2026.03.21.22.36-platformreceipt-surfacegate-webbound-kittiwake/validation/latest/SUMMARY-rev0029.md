# rev0029 validation summary

Passed:
- `python -m py_compile scripts/playwright_browsers.py scripts/playwright-browsers.py scripts/doctor.py scripts/e2e-fixturelab.py scripts/e2e_fixturelab.py tests/test_playwright_browsers.py tests/test_e2e_fixturelab.py`
- `pytest -q tests/test_playwright_browsers.py::test_parse_playwright_install_dry_run_reports_browser_packages tests/test_playwright_browsers.py::test_install_playwright_browser_archive_prefers_expected_install_name tests/test_playwright_browsers.py::test_import_cft_into_playwright_cache_uses_expected_playwright_install_name tests/test_playwright_browsers.py::test_local_playwright_browser_installations_support_headless_shell_package tests/test_playwright_browsers.py::test_sync_playwright_browser_packages_uses_archives_for_expected_packages tests/test_playwright_browsers.py::test_sync_playwright_browser_packages_uses_same_version_local_cft tests/test_e2e_fixturelab.py::test_wait_for_probe_result_playwright_parses_probe_json tests/test_e2e_fixturelab.py::test_wait_for_probe_result_playwright_omits_is_local_when_not_supported tests/test_validate_release.py tests/test_native_host.py -vv`
- `npm --prefix extension run typecheck`
- `npm --prefix extension run build`
- `python scripts/playwright-browsers.py dry-run --pretty`
- `python scripts/playwright-browsers.py sync --root validation/latest/tmp-pw-sync-rev0029 --archive validation/latest/rev0029-sync-fixtures/chrome-linux64.zip --archive validation/latest/rev0029-sync-fixtures/chrome-headless-shell-linux64.zip --include-headless-shell --pretty`
- `python scripts/playwright-browsers.py inspect --root validation/latest/tmp-pw-sync-rev0029 --pretty`
- `python scripts/doctor.py --pretty`

Not proven here:
- no fresh successful Playwright persistent-context proof against a real downloaded bundled browser
- no fresh live browser/native-host round-trip
- `python -m playwright install chromium` still fails in this container on DNS (`EAI_AGAIN`), which is preserved as a validation artifact
