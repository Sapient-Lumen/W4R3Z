# rev0028 validation summary

Passed:
- `python -m py_compile scripts/playwright_browsers.py scripts/playwright-browsers.py scripts/doctor.py scripts/e2e-fixturelab.py scripts/e2e_fixturelab.py`
- `pytest -q tests/test_playwright_browsers.py::test_parse_playwright_install_dry_run_reports_browser_packages tests/test_playwright_browsers.py::test_install_playwright_browser_archive_prefers_expected_install_name tests/test_playwright_browsers.py::test_import_cft_into_playwright_cache_uses_expected_playwright_install_name tests/test_playwright_browsers.py::test_local_playwright_browser_installations_support_headless_shell_package`
- `pytest -q tests/test_e2e_fixturelab.py::test_discover_playwright_browser_install_prefers_bundled_cache tests/test_e2e_fixturelab.py::test_playwright_extension_launch_plan_uses_bundled_executable tests/test_e2e_fixturelab.py::test_playwright_extension_launch_plan_skips_system_fallback_by_default tests/test_e2e_fixturelab.py::test_playwright_extension_launch_plan_allows_system_fallback_when_opted_in`
- `pytest -q tests/test_dev_tools.py::test_doctor_script_reports_manifest_and_wrapper`
- `pytest -q tests/test_dev_tools.py::test_cli_doctor_command_runs_with_pythonpath`
- `pytest -q tests/test_validate_release.py`
- `pytest -q tests/test_native_host.py`
- `npm --prefix extension run typecheck`
- `npm --prefix extension run build`
- `python scripts/playwright-browsers.py dry-run --pretty`
- `python scripts/playwright-browsers.py inspect --pretty`
- `python scripts/doctor.py --pretty`

Not proven here:
- no fresh successful live browser/native-host round-trip
- no successful Playwright persistent extension proof against a real cached browser package
