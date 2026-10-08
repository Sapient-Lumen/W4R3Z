# Automation lab notes

GlassTTY is user-driven first, but it should preserve a future lane for headed or headless automation experiments.

## Current stance

- primary workflow: browser open and visible
- primary browser family: Chromium
- future automation test lane: Playwright with bundled Chromium

## Why Chromium matters here

Playwright documents Chrome extension support for Chromium persistent contexts, and notes that Google Chrome and Microsoft Edge removed the command-line flags needed to side-load extensions. That makes bundled Chromium the practical extension automation target later.

## Consequence for repo design

Keep the real product architecture independent from the automation stack:
- extension and native host are the product path
- Playwright is a later test/automation layer, not the foundation
