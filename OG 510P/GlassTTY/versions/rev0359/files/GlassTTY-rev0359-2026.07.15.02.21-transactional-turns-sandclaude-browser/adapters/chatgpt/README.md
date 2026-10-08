# ChatGPT adapter

This folder is for ChatGPT-specific logic, notes, and fixtures.

## Adapter goals

- confirm the current official browser route and receiver posture
- locate the current composer using accessible, user-facing semantics first
- write and submit one harmless probe turn with evidence that survives drift
  review
- locate the latest assistant turn without depending on brittle class names
- report useful fallback candidates when selectors drift

## Current implementation shape

- URL match: `https://chatgpt.com/*`
- route baseline: prefer the plain chat/home route before Projects, GPT builder,
  Canvas, or other richer modes
- composer heuristics: role/textbox, `textarea`, `contenteditable`,
  `contenteditable="plaintext-only"`, `data-placeholder`, and ProseMirror-like
  editable roots
- submit heuristics: visible scoped button with accessible name resembling
  `Send`, plus scoped `form button[type="submit"]` fallback
- latest-turn heuristics: prefer explicit `data-message-author-role="assistant"`
  on the node or ancestor, then resolve latest visible assistant-like DOM order

## Known weakness

The current notes are deliberately conservative. Real ChatGPT fixtures should
replace hand-written assumptions quickly, especially for route gating, composer
affordances, and latest-turn readback.

## Expected next artifacts

- small surface capsule from `tools/chatgpt-surface-capsule.js`
- audited capsule output from `scripts/chatgpt-surface-report-audit.py`
- saved DOM fixture from `tools/chatgpt-surface-megathing.js`
- initial route/composer baseline bundle
- one compose/submit/read-latest support bundle
- posture matrix for distinguishing baseline-safe home shells from richer
  branches
- route-witness receipt for grading witness quality and proof readiness
  separately from branch classification
- composer-witness receipt for grading writability and readback separately from
  merely discovering a candidate textbox
- breakage notes when ChatGPT UI changes
- support-claim receipt for bounding the strongest honest browser/auth/route
  support language
