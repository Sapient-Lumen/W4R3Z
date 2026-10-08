# Next work after rev0871

1. Define and implement an authenticated terminal receiver record, with exact
   operation, sender receipt, receiver actor epoch, channel binding, key epoch,
   and terminal/nonterminal outcome.
2. Build a receiver idempotency/effect owner so crash after effect but before
   acknowledgment cannot duplicate externally visible work.
3. Add a trusted clock/high-water owner and an automatic heartbeat/wake
   scheduler. Test rollback, jump, process death, and restart boundaries.
4. Persist retry provenance or replace absolute caller-supplied retry time with
   a pure bounded retry policy carrying attempt/age/dead-letter limits.
5. Add a point-read/incremental SQLite owner while retaining the current
   O(history) owner as a differential oracle. Measure rows, WAL, I/O, and lock
   duration rather than calling logical byte counts physical budgets.
6. Exercise a two-process sender/receiver crash matrix only after the receiver
   authority model is explicit. Do not resurrect the removed unintegrated wire
   side branch as an API-only layer.
7. Continue toward actor membership, key lifecycle, peer authentication,
   causal stability, compaction, and the actual anonymity/privacy protocol.
