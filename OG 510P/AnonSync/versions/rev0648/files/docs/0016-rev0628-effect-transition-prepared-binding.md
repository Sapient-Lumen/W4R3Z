# rev0628 — prepared-entry-bound effect transitions

## Problem

rev0626 introduced append-only terminal effect transitions and rev0627 added a verified pending-effect recovery report. The remaining seam was that a terminal transition identified a prepared effect only by `effect_idempotency_key`.

That was better than nothing, but it allowed a stale/copied key to be the only evidence that a worker was closing the prepared ledger row it had actually inspected.

## Change

rev0628 requires terminal transitions to provide:

- `effect_idempotency_key`
- `prepared_sequence`
- `prepared_entry_hash`
- terminal state
- downstream result digest
- transition reason

The pending-effect report format advances to `anonsync-sqlite-effect-pending-report-v2` and includes `entry_hash` for each pending prepared decision. SQLite/WAL advances to schema v6 and stores `prepared_sequence` plus `prepared_entry_hash` on every terminal transition. Those fields are included in the effect-transition hash material.

## Safety properties

- A missing prepared sequence fails closed.
- A malformed prepared entry hash fails closed.
- A stale sequence fails closed.
- A stale or mismatched entry hash fails closed.
- The read-only snapshot verifier recomputes and checks the transition chain and prepared-row binding.

## Remaining boundary

This is still local recovery evidence. It does not prove that the downstream service applied the effect, and it does not implement a distributed exactly-once protocol.
