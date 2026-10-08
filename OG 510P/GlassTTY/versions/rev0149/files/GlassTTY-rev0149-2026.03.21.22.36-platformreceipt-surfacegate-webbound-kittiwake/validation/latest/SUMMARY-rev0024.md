# rev0024 validation summary

## Passed

- Python compile checks for the new Chrome-for-Testing helper scripts and smoke-lane script
- `pytest -q tests/test_browser_binaries.py tests/test_e2e_fixturelab.py -k 'not fixturelab_e2e_smoke'`
- `pytest -q tests/test_dev_tools.py tests/test_validate_release.py tests/test_native_host.py`
- `npm run typecheck`
- `npm run build`
- `python scripts/doctor.py --pretty`
- `python scripts/chrome-for-testing.py inspect --pretty`

## Best-effort browser smoke

`python scripts/e2e-fixturelab.py --timeout 10 --output validation/latest/e2e-fixturelab-rev0024.json`

Result:
- native-host install step succeeded after fixing execute permission handling for `install-native-host.sh`
- browser choice resolved to system Chromium (`/usr/bin/chromium`) because no local Chrome-for-Testing bundle is installed here
- both `headless-new` and `xvfb` launch attempts were recorded
- the run still failed with: `extension page or service worker was not confirmed through Playwright persistent launch or CDP in any browser mode`

This is a real improvement over the initial rev0024 smoke failure, but it is still not a successful live-browser proof.
