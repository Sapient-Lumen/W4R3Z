# Structural audit rev0369

Rev0369 was scoped to reduce operational risk rather than enlarge doctrine. It adds executable acquisition controls and a reproducible hotpath build path.

## P0 risk addressed

The records request path previously existed as a queue but was not sendable or deadline-bound. Rev0369 adds request templates, a meeting-capture runbook, absolute release/watch clocks, and a blocker-to-request map.

## P0 risk still open

No real evidence packet exists. The evidence state remains claim-frozen. The public meeting and release clocks are not findings.

## Refactor performed

The rev0368 hotpath capsule was useful but manually curated. Rev0369 introduces a source-list-driven builder that regenerates the hotpath SQLite and capsule, and a validator that checks required tables, hashes, and duplicate paths.

## Waste avoided

The full cube still contains large historical matrices and SQLite mirrors. Rev0369 does not delete them, but the active path now points operators to the bounded hotpath artifacts before whole-cube scans.
