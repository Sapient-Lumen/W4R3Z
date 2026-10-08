# Compaction audit and hard negatives

Compaction audit treats evidence deletion as a protocol boundary.  Even when
terminal receipt, idempotency repair, finality, and prune guard all accept, a
compaction plan must preserve the terminal receipt digest, idempotency repair
digest, finality digest, prune digest, and every hard-negative digest that
remains live for that boundary.

The audit rejects terminal-receipt drops, idempotency-repair drops,
finality/prune drops, hard-negative drops, digest drift, and boundary drift.
