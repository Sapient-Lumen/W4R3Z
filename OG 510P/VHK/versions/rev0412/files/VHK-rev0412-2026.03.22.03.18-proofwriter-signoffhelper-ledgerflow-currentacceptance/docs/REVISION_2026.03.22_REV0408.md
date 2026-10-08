# Revision 0408 — dispatch receipt desktop-session truth

Date: 2026-03-22
Revision: 0408

## What changed

- warm dispatch receipts now capture `desktop_session_contract` when they are written
- `latest-dispatch-json` now compares the newest receipt against the current shell session
- `macro-dispatch-history-board-json` now distinguishes contract drift, desktop-session drift, and resident-daemon drift
- legacy receipts without a session witness remain readable instead of being forced stale

## Why it matters

VHK is explicitly i3/X11-first and session-bound. A clean checked-dispatch receipt from another `DISPLAY`/`I3SOCK` session is still useful history, but it is not current proof for the live desktop the private LLM is about to operate. This revision makes the warm dispatch lane say that directly.
