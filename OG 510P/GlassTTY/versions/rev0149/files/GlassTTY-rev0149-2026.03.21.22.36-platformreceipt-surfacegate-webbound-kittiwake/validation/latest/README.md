# validation/latest

Current rev0029 validation artifacts live here.

Read these first:

- `SUMMARY.md` — human summary of what passed and what failed honestly
- `doctor-rev0029.json` — current environment + Playwright sync preview
- `playwright-dry-run-rev0029.json` — the current Playwright package matrix (`chromium-1208` / `chromium_headless_shell-1208` here)
- `playwright-sync-rev0029.json` — one-shot package sync proof against local fixture archives
- `playwright-install-rev0029.stderr` — honest failure of the real networked Playwright installer in this container
- `test_playwright_sync-focused-rev0029.txt` — focused pytest evidence for the new sync + CDP helper work
