# rev0083 focused summary

- baseline: `GlassTTY-rev0082-2026.03.17.03.52-playwrightaudit-shadowtruth-versionlock-wryneck.zip`
- focus: Playwright cache repair for shadow installs and broken `.links` registry entries
- targeted pytest: passed (`tests/test_playwright_browsers.py` repair-focused subset, `tests/test_dev_tools.py` doctor-focused subset)
- extension typecheck/build: passed
- real temp-root proof: a manual `chromium-shadow-*` install plus a broken `.links` entry were repaired, and raw `python -m playwright install --list` then showed `chromium-1208`
- package verify: pending final zip verification
- honest gap: still no live Chromium/native-host/browser round-trip or successful direct Playwright browser download in this container
