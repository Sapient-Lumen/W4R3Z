# Open questions

Revision: rev0059.

## Runtime frontiers

1. Can two same-origin contexts coordinate OPFS writes through Web Locks without hidden overlap or stale lock recovery problems?
2. What is the cheapest organic storage-pressure or eviction proof that does not waste cloudtainer disk?
3. Should OPFS sync-access-handle storage-lane behavior graduate after the async abrupt-kill and quota boundaries are stable?
4. What recovery policy should reopen a storage lane after quota/health failure without pretending automatic recovery is proven?

## Browser/test facility

1. Should browser proofs keep one browser per risky slice, or share a browser only inside explicitly modeled two-launch/coordination probes?
2. Should the cleanup audit grow from process-table checks into temp-profile directory budget checks?
3. Which browser-heavy proofs are valuable enough to run every session by explicit id, while keeping broad release browser-light?

## Cloudtainer process posture

1. Never rely on background browser/server state across turns. Every proof should own setup and teardown in one command.
2. Package-release should keep running process cleanup and artifact budget checks so failures become visible before zip creation.
3. Future work should reduce hand-edited manifest bulk, but only after current runtime proofs remain easy to select by id.
