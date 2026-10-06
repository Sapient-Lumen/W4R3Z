# Storage-lane late-settlement contract audit slice

Revision: rev0069  
Task: `facility:storage-lane-late-settlement-contract-audit`

## Purpose

This audit keeps the late-settlement recovery gate wired into the cube without making browser-heavy checks part of broad release. It checks runtime hooks, proof tools, docs, manifest entries, impact-map routing, surface inventory entries, and package/Makefile scripts.

## Required hooks

- `unsettledTimedOutOperations()` and `waitForTimedOutOperationsSettled()` on the storage-lane executor.
- `storage-lane:operation-timeout-unsettled` and `storage-lane:late-provider-settlement` trace events.
- `requireTimedOutOperationsSettled` and `timed-out-operation-still-unsettled` in `recoverWhenStoreSettled()`.
- Release proof `scheduler:storage-lane-late-settlement-recovery-gate-proof`.
- Browser proof `browser:opfs-web-lock-late-settlement-recovery-gate-proof`.

## Non-claims

The audit does not launch a browser and does not prove OPFS behavior by itself. It only prevents wiring drift around the runtime and proof surfaces.

Cross-browser, quota, eviction, and crash behavior are out of scope for this audit.
