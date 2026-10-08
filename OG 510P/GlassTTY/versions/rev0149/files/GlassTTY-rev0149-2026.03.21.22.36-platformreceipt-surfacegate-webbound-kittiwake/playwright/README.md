# Playwright lab

This directory is intentionally light-weight for now.

## Purpose

Keep a clean landing zone for future Chromium automation and extension smoke tests without making Playwright the foundation of the real product.

## Planned first uses

- launch bundled Chromium with a persistent context
- load the unpacked GlassTTY extension
- verify the side panel and service worker boot
- run fixture-based smoke tests against local HTML pages before touching live sites

## Why bundled Chromium

Chrome extension support in Playwright is documented for Chromium persistent contexts, and Google Chrome / Microsoft Edge no longer support the old sideload flags in the same way.

## First future files to add here

- `package.json`
- `playwright.config.ts`
- `tests/extension-smoke.spec.ts`
- `fixtures/` symlink or import path notes
