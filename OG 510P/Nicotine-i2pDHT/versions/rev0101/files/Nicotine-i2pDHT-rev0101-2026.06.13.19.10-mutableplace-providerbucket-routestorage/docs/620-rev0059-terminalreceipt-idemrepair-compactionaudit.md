# rev0059 — terminalreceipt-idemrepair-compactionaudit

This revision keeps working at the post-finality edge.  rev0058 gave the cube a
finality ledger, retry escrow, and prune guard.  rev0059 adds a stricter local
layer: terminal receipts, idempotency repair plans, compaction audit plans, and a
folded settlement/attestation/tombstone-repair branchlet.

The main guess is that terminality is not enough.  A node also needs a receipt
that binds terminality to the exact action, scope, request, payload, idempotency
key, prune plan, and finality marker.  Repair and compaction then need their own
joined reports so a restart, retry, or cleanup path cannot erase lineage.

Strong sentence: terminality, repair, and compaction are separate local
permissions; none may launder stale retry/dead-letter memory into clean terminal
truth.
