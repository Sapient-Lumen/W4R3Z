# rev0094 focused validation

- `python -m py_compile scripts/e2e-fixturelab.py scripts/e2e_fixturelab.py scripts/mv3-worker-resume.py scripts/mv3_worker_resume.py`
- `pytest -q tests/test_e2e_fixturelab.py tests/test_cdp_inspect.py`
- `npm --prefix extension run typecheck`
- `npm --prefix extension run build`
- `python scripts/archive-audit.py --pretty .`
- one honest best-effort `GLASSTTY_PLAYWRIGHT_ALLOW_SYSTEM_EXECUTABLE=1 python scripts/mv3-worker-resume.py --output validation/rev0094-focused/live-mv3-resume-report.json --timeout 15` attempt
- `python scripts/verify-package.py <final zip>`

The live restart attempt did not complete in this container. It reached extension build plus native-host install, then was terminated by signal 15 during the browser phase.
