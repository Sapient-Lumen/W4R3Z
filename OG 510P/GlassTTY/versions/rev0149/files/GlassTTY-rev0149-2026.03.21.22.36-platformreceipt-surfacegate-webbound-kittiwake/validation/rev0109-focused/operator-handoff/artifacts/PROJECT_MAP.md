# Project map

## Purpose

This file is the fast orientation map for humans and LLMs.

## Read order

1. `README.md`
2. `STATUS.md`
3. `MEMORY.md`
4. `DECISIONS.md`
5. `AGENTS.md`
6. `TASKS.md`
7. `ARCHIVE_MANIFEST.json`
8. `.llm/SESSION_START.md`

## High-value directories

- `extension/` — Chromium MV3 extension
- `daemon/` — Python native host and local broker socket
- `adapters/` — app-specific notes and fixtures
- `docs/` — durable architectural reasoning
- `scripts/` — Chromium profile, install, packaging, archive-refresh, readiness, and operator-handoff helpers
- `tests/` — executable checks
- `playwright/` — future Chromium automation lab landing zone
- `.llm/` — session hygiene for future model operators

## Current implementation hotspots

- `extension/src/background/main.ts`
- `extension/src/content/main.ts`
- `extension/src/adapters/claude.ts`
- `extension/src/sidepanel/main.ts`
- `daemon/src/glassttyd/native_host.py`
- `daemon/src/glassttyd/broker.py`
- `daemon/src/glassttyd/cli.py`

## Current generic vs specific split

### Generic core
- native messaging bridge
- local broker socket
- JSON envelope protocol
- CLI request and watch model
- Chromium profile tooling
- supported-tab targeting

### Claude-specific first adapter
- prompt composer detection
- latest visible output detection
- candidate-debug heuristics
- transcript delta watcher

## Most important unverified path

`CLI -> UNIX socket -> native host -> extension service worker -> selected supported browser tab -> extension service worker -> native host -> CLI`
