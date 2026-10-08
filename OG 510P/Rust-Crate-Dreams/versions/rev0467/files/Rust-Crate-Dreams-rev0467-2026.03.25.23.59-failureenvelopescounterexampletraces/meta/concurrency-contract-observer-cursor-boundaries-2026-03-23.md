# Concurrency Contract Kit observer-cursor boundaries — 2026-03-23

This note prevents the new observer-cursor lane from collapsing into neighboring lanes.

## Keep these lanes separate

### A. Observer cursor is not delivery audience
Audience asks **who may observe one unit**.
Observer cursor asks **whether each observer advances its own progress frontier or competes for one shared frontier**.

### B. Observer cursor is not consumption claim
Claim asks **whether one observer taking a unit excludes others**.
Cursor asks **how observer progress is tracked across time**.
A surface can be single-delivery and still differ between fixed single-consumer, shared competitive pool, or independent receiver-local cursors.

### C. Progress isolation is not backlog pressure
Backlog pressure asks **what the surface does when producers outrun consumers**.
Progress isolation asks **whose experience changes when one observer slows down**.
A lagging receiver can trigger self-local rebasing without blocking senders in the same way a bounded queue backpressures producers.

### D. Per-receiver cursor is not full replay support
A receiver with its own retained-history cursor is not promised full origin replay.
It may still start late, lag, or be rebased to the oldest retained value.

### E. Wake-only notification is not a degenerate data cursor
If a surface carries no data and only affects wake eligibility, cursor/posture language should stay explicitly wake-only instead of silently pretending there is an event stream cursor.

## Claims to reject

Reject bundle drafts that silently equate:

- cloneable receivers with independent per-observer cursors,
- single-delivery competition with lag-local per-receiver progress,
- per-receiver retained-history cursors with full replay history,
- wake-only notification with data-bearing cursors,
- fixed single-consumer channels with “manual-review maybe multi-observer” posture.
