# Concurrency Contract Kit join-horizon boundaries — 2026-03-23

This note prevents the new join-horizon lane from collapsing into neighboring lanes.

## Keep these lanes separate

### A. Late-joiner admission is not delivery audience
Audience asks **who can observe one unit**.
Admission asks **whether a new observer can enter after the surface already exists**.

### B. Join-start baseline is not delivery memory
Memory asks **what the surface remembers when nobody is ready**.
Join-start asks **what a newly admitted observer starts with**.
A stored permit, current snapshot, or current tail can come from memory, but the join baseline is still a separate receiver-facing claim.

### C. Join-start baseline is not post-close availability
Post-close availability asks **what remains observable after closure**.
Join-start asks **what a newly admitted observer sees at admission time**, regardless of whether the surface is closed.

### D. Resubscribe-from-tail is not full history fanout
A receiver that resubscribes from the current tail is not promised the current receiver’s pending queue, and is not promised full replay history.

### E. Current-waiters-only notify is not late-join support
If a method only reaches already registered waiters and stores no future permit, that is not a future-joiner route.

## Claims to reject

Reject bundle drafts that silently equate:

- `subscribe()` with current-snapshot semantics,
- current-snapshot subscribe with future-only subscribe,
- resubscribe-from-tail with replay-from-origin,
- stored-permit wake memory with current-waiters-only wake,
- fixed-pair channels with “manual-review maybe late joiners”.
