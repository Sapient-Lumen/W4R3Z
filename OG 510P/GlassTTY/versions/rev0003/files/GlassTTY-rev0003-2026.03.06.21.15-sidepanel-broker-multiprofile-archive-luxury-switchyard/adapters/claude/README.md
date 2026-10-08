# Claude adapter

This folder is for Claude.ai-specific logic, notes, and fixtures.

## Adapter goals

- locate the current prompt composer
- locate the latest assistant turn
- report useful debug candidates when selectors drift
- stay isolated from generic protocol naming

## Current implementation shape

- URL match: `https://claude.ai/*`
- prompt heuristics: `textarea`, `[contenteditable="true"]`, `[role="textbox"]`
- output heuristics: coarse fallback over `main`, `article`, and `[role="main"]`
- send heuristics: visible button whose text or aria-label looks like `send`

## Known weakness

The current output extraction is intentionally crude and must be replaced with real Claude fixtures from live pages.

## Expected next artifacts

- selector notes
- saved DOM fixtures
- extraction heuristics
- breakage notes when Claude UI changes
