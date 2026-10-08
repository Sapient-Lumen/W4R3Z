# ROADMAP

## Phase 0 — Bootstrap

- scaffold repo
- define protocol envelope
- build native-host hello world
- create Chromium profile launcher

## Phase 1 — Claude adapter minimum viable bridge

- detect prompt composer
- detect latest assistant turn
- implement read current prompt
- implement read latest output
- implement write prompt text
- prove broker-backed CLI requests

## Phase 2 — State streaming

- mutation observer for transcript deltas
- JSONL event log
- CLI watch mode
- state snapshot caching
- side-panel live bridge status

## Phase 3 — Robustness

- selector fallback registry
- DOM candidate scoring and debug views
- fixture-based tests from saved HTML snapshots
- better error surfaces
- multiple isolated profile workflows

## Phase 4 — Generalization

- second browser-app adapter
- generic page introspection helpers
- transport abstraction if Rust rewrite begins
- richer adapter capability model

## Phase 5 — Automation lab

- headed automation experiments in Chromium
- Playwright extension-aware testing
- optional headless workflows where appropriate
