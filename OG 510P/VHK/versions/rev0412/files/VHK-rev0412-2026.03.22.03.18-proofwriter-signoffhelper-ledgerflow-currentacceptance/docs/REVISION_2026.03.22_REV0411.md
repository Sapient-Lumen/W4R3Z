# Revision 0411 — desktop-session-bound durable acceptance

Date: 2026-03-22
Revision: 0411

## What changed

- extended `runtime_acceptance_contract` with `desktop_session_contract_digest`
- `current_runtime_acceptance_contract` now captures the current X11/i3 desktop-session digest alongside replay/dispatch proof and resident-runtime witness data
- durable runtime signoff now goes stale when the current `DISPLAY`/`I3SOCK` session changes underneath an older acceptance row
- acceptance-ledger, runtime-board, and author-loop surfaces now expose that drift through the existing `runtime_signoff` contract path

## Why it matters

Revisions 0407 and 0408 made replay proof and dispatch receipts session-bound, and revision 0410 made durable signoff resident-daemon-bound. This revision closes the remaining X11/i3-specific stale-success hole: durable acceptance itself is now session-bound too.

That means operator signoff no longer silently survives a desktop-session move just because no fresh run or receipt has been written yet.
