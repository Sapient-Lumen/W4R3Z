# Automation lab notes

GlassTTY is user-driven first, but it should preserve a future lane for headed or headless automation experiments.

## Current stance

- primary workflow: browser open and visible
- primary browser family: Chromium
- primary in-container proof lane today: raw Chromium plus DevTools/CDP inspection
- secondary lab lane: Playwright persistent-context launch with the Playwright-managed browser package when available, while Playwright-over-CDP remains an experimental observer lane

## Why Chromium matters here

Playwright documents Chrome extension support for Chromium persistent contexts, and notes that Google Chrome and Microsoft Edge removed the command-line flags needed to side-load extensions. That keeps Chromium as the practical automation target.

## What rev0021 and rev0026 learned

- raw headless Chromium with the unpacked extension can now be proven in this container through `/json/version` and `/json/list`
- a manual Playwright `connect_over_cdp()` attach also works in this container, but the attached context currently surfaces `chrome-error://chromewebdata/` instead of the expected probe page
- because of that mismatch, raw CDP remains the primary proof claim here and Playwright remains an experimental observer lane

## Consequence for repo design

Keep the real product architecture independent from the automation stack:
- extension and native host are the product path
- raw Chromium+CDP is the current pragmatic proof path in this archive
- Playwright is a lab layer, not the foundation

## What rev0027 learned

- browser acquisition is a separate problem from browser launch: this container has Playwright installed, but `python -m playwright install chromium` fails on DNS (`EAI_AGAIN`), even though `python -m playwright install --dry-run chromium` can still reveal the expected package names
- because of that, GlassTTY now keeps an explicit offline/local-archive seeding path for both Chrome for Testing and the Playwright Chromium cache
- this makes the automation lab more archive-friendly and better aligned with the repo's general hermetic/LLM-handoff goals


## What rev0029 learned

- knowing the expected Playwright package names is useful, but not sufficient; the lab also needs a one-shot way to align local archives or local Chrome-for-Testing installs with that package matrix
- because Playwright 1.58 exposes `connect_over_cdp(..., is_local=True)`, GlassTTY can now make that local-observer path slightly more faithful without changing its main proof claims
- in this container the networked Playwright installer still fails on DNS, so explicit cache alignment remains more important than yet another install hint
