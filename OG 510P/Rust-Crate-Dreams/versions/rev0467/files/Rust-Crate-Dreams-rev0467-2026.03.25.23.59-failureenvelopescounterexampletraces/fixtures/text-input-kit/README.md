# text-input-kit fixtures

This fixture family exists to keep **transaction truth**, **selection truth**, and **backend-capability truth** reviewable for **P-0027 text-input-kit**.

## Core artifact classes

- `ime-transaction.report.json` — what preedit/commit/cancel/replacement-range truth the engine observed and applied
- `selection-contract.report.json` — what grapheme/word/line/anchor-head behavior the engine claims
- `backend-capability.receipt.json` — what the active adapter can honestly support on this platform/runtime

## Scenario themes

- native IME/key-event overlap or dedup edges
- web hidden-input fallback boundaries
- emoji/ZWJ and grapheme-cluster deletion correctness
- future bidi/editor-policy boundaries where manual review still matters

## Added 2026-03-20

- `web-edit-path.receipt.json` — which surface really owns focus/composition state on the web, and whether a hidden-input / EditContext / DOM-delegate path is in use
- `selection-geometry.report.json` — whether caret / selection / character bounds, candidate anchoring, provisional rendering, and a11y mirror truth are reviewable

## Added scenario themes

- EditContext-backed canvas flows that still owe an offscreen / parallel accessibility mirror
- native IME backends where leaked release events must be normalized explicitly rather than inheriting a clean transaction story
