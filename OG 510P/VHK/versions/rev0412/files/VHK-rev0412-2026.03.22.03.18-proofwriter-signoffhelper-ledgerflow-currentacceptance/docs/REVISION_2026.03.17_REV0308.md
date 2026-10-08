# REV0308 — installed-lane runtime health verdicts

This revision takes the installed-lane status bridge one step beyond session
readiness and teaches it to preserve **runtime health** explicitly.

## What changed

- Added `src/vhk/project/session_runtime_health.py`
- Extended the native installed launcher status/report path so it now captures:
  - one runtime-health verdict alongside the readiness verdict
  - restart-churn signals from nearby user-unit state (`NRestarts`,
    `start-limit-hit`, active/sub states)
  - better separation between healthy socket-owned lanes, stopped lanes,
    missing-unit lanes, and lanes with no owned long-lived service
- Extended `gen-support-pack` so support guidance/checklists now ask for both
  readiness and runtime-health verdicts from the installed lane before jumping
  to heavier host packets

## Why it matters

A Linux-native automation tool should not force operators to infer “restart
storm” or “idle but healthy socket lane” from raw `systemctl` text every time.
This revision gives VHK one lighter operator truth for that question directly in
its installed status surfaces.
