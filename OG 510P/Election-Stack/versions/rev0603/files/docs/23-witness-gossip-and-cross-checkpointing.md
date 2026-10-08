# Witness gossip & cross-checkpointing (CT-style, election-grade)

**Track:** A (Deployable core)


This doc makes witnesses enforceable rather than ceremonial.

## Goal
Detect (and publicly prove) any of:
- **equivocation**: PBB shows different histories to different clients (“split view”);
- **rollback**: serving older tree heads to hide newer ballots;
- **selective inclusion**: intake accepted, ballot never included.

## Objects
- **STH**: Signed Tree Head (tree_size, root_hash, timestamp, log_id, signature)
- **Checkpoint**: witness-quorum cosigned STH (policy constrained)
- **ForkProof**: evidence the log produced inconsistent histories

See JSON Schemas in `schemas/`.

## Witness gossip rules (MUST)
1. Every witness MUST fetch STHs from:
   - at least one PBB node directly, AND
   - at least one peer witness.
2. Witnesses MUST verify consistency between STHs.
3. On inconsistency, witnesses MUST publish a ForkProof and alert all peers.
4. Witnesses MUST publish their latest STH observations and checkpoints to public endpoints (mirrored by peers).

## Checkpoint policy (MUST)
A “FINAL” receipt requires a Checkpoint satisfying:
- quorum Q-of-W witnesses (e.g., 7-of-11),
- diversity constraints (e.g., ≥1 from each of: election authority, opposition party, civil society, academia),
- timestamp monotonicity; rollback forbidden.

## Cross-checkpointing (SHOULD)
To harden against collusion:
- Each witness SHOULD cross-log checkpoints to at least one independent archive/log.
- If cross-logging is used, publish inclusion proofs for cross-log entries.

## Client verification (MUST)
Clients MUST NOT trust a single node:
- verify inclusion proofs against an STH that is either witness-confirmed or checkpointed,
- query multiple witnesses for the latest checkpoint head.

## Failure handling
- If witnesses disagree: receipts must degrade to NOT RECORDED / NOT FINAL.
- If quorum cannot be reached: invoke recovery path (paper-of-record; supervised override where available).
- If ForkProof exists: treat PBB as compromised; follow incident procedure.