# Apparently new / unmentioned findings — rev0100

## P1/P2 — Priority lifecycle cleanup can still be dropped when the retry shelf is full of ordinary preserved payloads

**Status:** apparently new exact mechanism in the cube hardening layer; public searches did not find a matching report for this priority-admission failure.

Rev0099 fixed head-of-line blocking by placing priority cleanup/rollback events ahead of ordinary preserved payload/request events. Rev0100 found the next admission-level gap: if the bounded `_main_thread_lifecycle_event_retries` shelf is already at its item or byte limit with ordinary preserved events such as `message-user` or incoming request intent, a later priority cleanup event can still be rejected before insertion.

**Why it matters:** priority lifecycle events are the small events that release or roll back critical state: `file-connection-closed`, `peer-message-unsent`, `peer-response-unsent`, `server-message-unsent`, `peer-connection-error`, and related cleanup paths. Dropping one of those in order to preserve an ordinary retry payload can leave stale file-transfer state, stale peer init state, stale grants, or stale request ledgers.

**Implemented in rev0100:**

- Added `_can_queue_main_thread_lifecycle_event_retry()` as the single admission predicate.
- Added `_drop_main_thread_lifecycle_event_retry_at()` with byte-accounting release.
- Added `_make_room_for_priority_main_thread_lifecycle_event_retry()`.
- Priority events may evict nonpriority retry entries, starting from the newest/lowest-value ordinary retry.
- Existing priority events are not evicted; priority ordering remains preserved.
- Count and byte caps still apply.
- Added regressions for ordinary-payload eviction and priority-only rejection.

**How to present upstream:** current upstream still uses an unbounded `SimpleQueue` bridge, so this is primarily a cube/hardening-layer correctness issue. The upstream-relevant invariant is important: if the bridge is ever bounded, cleanup/rollback events need both priority ordering and priority admission over ordinary preserved payload/request retries.
