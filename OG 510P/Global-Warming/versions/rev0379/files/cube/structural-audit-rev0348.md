# Structural audit — rev0348

Rev0348 adds a live-intake operator console above the rev0347 quarantine folders.

## Key correction

The prior quarantine folder system was ready to receive evidence, but an exercise-week operator still had to infer packet state from many tables. Rev0348 materializes a single 60-row console with packet state, synthetic-retirement blocker, payload counts, loss cap, next operator action, and public-claim effect.

## Current state

* 60 packets remain under loss cap.
* 24 packets still have seeded synthetic dry-run payloads that require retirement/replacement before any real claim path.
* 0 packet rows allow automatic closure.
* 0 public-context-to-local-closure leaks are present in the scoped SQLite view.

## Remaining hard boundary

The console is an intake control, not evidence. Empty folders, synthetic files, public notices, dashboards, meeting statements, source IDs, and complete-looking local packets remain non-closure until adjudication, CAP/retest if applicable, independent verification, and claim-kernel release.
