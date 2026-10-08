# Checkpoint lane restart pressure

Checkpoints are convenient and dangerous.  A node may want to summarize witness caches, tombstones, revocation heads, provider ledger roots, custody roots, route leases, and journal tips so restart is fast.  A bad checkpoint can silently erase the memory that kept the node safe.

`checkpointlane.py` models signed local checkpoints as observations, not truth.  Acceptance requires:

- valid signer and validity window;
- monotonic generation;
- previous-checkpoint digest linkage;
- same-generation fork detection;
- rollback detection;
- hard-negative preservation for live tombstones and capability revocations;
- conflict detection for same kind/scope/sequence facts.

The hardest test is a checkpoint that links correctly but omits a live hard fact.  rev0029 quarantines it instead of treating the compact summary as safer than the older local memory.
