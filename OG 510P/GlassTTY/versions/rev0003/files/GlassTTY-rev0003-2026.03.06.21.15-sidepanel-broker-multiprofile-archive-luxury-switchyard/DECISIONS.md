# DECISIONS

## 2026-03-06 — Chromium first, Firefox no longer primary

### Decision
GlassTTY will target Chromium first.

### Why
- better alignment with future automation and extension-testing tooling
- easier long-run path toward headed/headless experimentation
- user accepted the tradeoff

### Consequence
Firefox can remain a secondary compatibility target later, but the repo and tooling will optimize for Chromium now.

---

## 2026-03-06 — Generic product, Claude-first adapter

### Decision
The product identity stays generic. Claude.ai is the first real working adapter, not the whole product.

### Why
- prevents project identity from collapsing into a one-off site hack
- keeps future adapters possible
- improves protocol and code hygiene

### Consequence
Shared protocol names and core docs must avoid Claude-specific naming unless inside adapter folders.

---

## 2026-03-06 — Archive as source of truth

### Decision
The repo archive is the durable memory layer for multi-session LLM work.

### Why
Chat logs are transient and fragmented.

### Consequence
Every meaningful session should leave behind updated repo memory files.

---

## 2026-03-06 — Local broker socket in v0

### Decision
The Python native host will expose a local UNIX-socket broker early rather than waiting for a later transport layer rewrite.

### Why
- it gives the CLI a clean local interface immediately
- it lets browser-originated events be watched from the terminal without scraping logs
- it creates a stable seam for a future Rust rewrite

### Consequence
The daemon now owns both browser-native-messaging framing and a local JSON-over-socket control plane.

---

## 2026-03-06 — Side panel as operator surface

### Decision
Use Chrome's side panel as the main in-browser diagnostics and control surface.

### Why
- it stays open alongside the active page
- it is less cramped than an action popup
- it pairs well with a user-driven browser-open workflow

### Consequence
Bridge state should be mirrored into `chrome.storage.local` so the side panel can survive service-worker restarts gracefully.
