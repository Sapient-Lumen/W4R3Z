# Idempotency repair lineage

Idempotency repair is the no-network plan for updating local idempotency memory
after terminal receipt acceptance.  A pure terminal path can repair with no
attempt lineage.  A retry-success path must carry the retry escrow digest,
dead-letter digest, carried-dead-letter digest, previous attempt number, and
resolved attempt number.

The risky cases are attempt regression, missing dead-letter carry, boundary
mismatch, digest drift, and hard-negative pressure.  A retry that eventually
settles must not look like a clean first attempt after compaction.
