# rev0025 validation summary

## Passed

- `python -m py_compile scripts/browser_binaries.py scripts/doctor.py scripts/e2e-fixturelab.py`
- `pytest -q tests/test_browser_binaries.py tests/test_e2e_fixturelab.py -k 'not fixturelab_e2e_smoke' tests/test_dev_tools.py tests/test_validate_release.py tests/test_native_host.py`
- `npm run typecheck`
- `npm run build`
- `python scripts/doctor.py --pretty`
- `python scripts/chrome-for-testing.py inspect --pretty`
- simulated CfT-136 doctor scenario written to `validation/latest/doctor-rev0025-cft136-simulated.json`

## Not newly proven here

- no successful real-browser/native-host round-trip claim
- no real local Chrome-for-Testing binary exercised in this container
- a fresh `scripts/e2e-fixturelab.py` run did not leave behind a stable new report artifact in this environment
- best-effort `scripts/e2e-fixturelab.py` attempt noted in `validation/latest/e2e-fixturelab-rev0025-note.txt`
