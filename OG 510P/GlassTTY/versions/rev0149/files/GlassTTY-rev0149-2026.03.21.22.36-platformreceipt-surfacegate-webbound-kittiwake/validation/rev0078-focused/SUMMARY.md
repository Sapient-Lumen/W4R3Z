# rev0078 focused summary

- pytest `tests/test_playwright_browsers.py`: ok
- pytest `tests/test_e2e_fixturelab.py`: not ok
- extension typecheck/build: ok
- honest smoke report: phase `finished`, `browser_mode_selected=headless-new`, `termination_signal=None`
- persistent Playwright lane: `ok=False`, `strategy=None`
- dry-run budget recorded in smoke report: `3.1` seconds

rev0078 improved the in-container smoke path enough to reach browser selection before signal 15 termination. It still does **not** prove a fresh live browser/native-host round-trip here.

- verify-package: `ok=True`
- archive audit identity: `ok=True`
