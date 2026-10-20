# ADR 0275: Bound tree-v2 history and retire writers exactly

Date: 2026-09-01

Status: accepted

## Context

ADR 0274 made the writable namespace a bounded full mesh, but every signed branch predecessor and
observation remained a permanent graph root. A lost or deliberately retired writer also remained
eligible to advance forever. That was safe against accidental deletion, but it made storage growth
unbounded and left no exact administrative end to a writer's branch.

The first three-daemon shadow exposed a second growth problem: a node published a new local branch
merely to acknowledge a newly observed remote frontier. Three quiet writers could therefore keep
echoing causality at one another without a filesystem change. A garbage collector cannot make an
unbounded acknowledgement protocol safe.

## Decision

Freeze branch-record version 2 as the checkpoint extension. A checkpoint is a normal signed local
branch with a current manifest and complete sorted observations, but it is an authenticated history
floor: graph traversal does not follow its predecessor or observation closure. It is legal only
when the current frontier has one conflict-free merged projection. Ordinary branch records remain
byte-identical version 1. Sending a frontier whose reachable closure contains a checkpoint requires
negotiated feature bit 31 (`state-sync-tree-checkpoint-v2`); a v1 peer never receives or silently
ignores one.

Stop publishing acknowledgement-only branches. Reconciliation publishes a local branch only for
initialization or a visible worktree change. A deterministic merged manifest is retained directly
for the signed workspace journal. The journal's active manifest and, during exchange, both pending
manifests are independent garbage-collection roots alongside its authenticated frontiers.

Add a stable-device-signed owner-local maintenance record containing bounded explicit record pins
and exact terminal writer cutoffs. Garbage-collection planning authenticates and walks:

1. every current writer pointer;
2. every explicit pin;
3. every active and pending signed workspace manifest and frontier;
4. predecessors and observations only until a signed checkpoint floor.

Inventory rejects weak or noncanonical directories, symlinks, non-regular objects, changed sizes,
and digest/signature mismatch. `sync-gc NAMESPACE dry-run` only reports the plan. `quarantine`
recomputes it under the namespace transaction and moves exact candidates with no-replace renames to
a private namespace-local quarantine. `sync-restore` reauthenticates every quarantined object before
moving it back. There is no purge or unlink mode.

`sync-pin` and `sync-unpin` name an exact branch-record digest and retain or release its complete
closure. `sync-checkpoint` creates the conflict-free local floor. `sync-retention` displays only
content-free maintenance facts.

`sync-writer-cutoff NAMESPACE WRITER_PUBLIC_KEY_HEX` first requires the local checkpoint to exactly
subsume that writer's current record. It then signs the terminal `(writer, generation, record)`,
removes the writer's current pointer, removes that principal from local bidirectional automation,
and refuses every later record from that writer. The writer remains in namespace policy so retained
historical signatures can still be verified. Every surviving owner must apply the cutoff locally;
this command is not a distributed membership transaction and does not revoke the principal's other
capabilities. General authority revocation remains a separate owner act.

Candidate sets remain bounded to one live candidate per writer and at most 16 candidates per path.
Checkpoint creation refuses an unresolved conflict rather than erasing an alternative.

## Consequences

Quiet convergence is now quiescent: receiving another branch may change the signed workspace
projection without manufacturing a new writer event. A later real edit uses that workspace's exact
frontier and therefore still observes the values the user saw.

Tree-v2 history and CAS bytes can be reclaimed recoverably after an explicit checkpoint, pins can
hold forensic or rollback material, and a departed writer can be fenced at one exact admitted
record. Tampering and partial maintenance fail closed; recovery never trusts a caller-supplied path.

The maintenance signature detects alteration but is not a hardware rollback witness. Quarantine is
not deletion, a cutoff is not group consensus, and checkpointing does not resolve a conflict. A
receiver verifies the checkpoint writer and compact snapshot but cannot replay history below the
floor; a fresh receiver may therefore bootstrap from one authorized writer's attestation without
multisignature agreement. A malicious authorized writer remains inside the threat boundary, so
operators should checkpoint only through controlled writers. Ignore rules, metadata portability,
malicious-fork/conflict-storm qualification, large-tree performance, hours-long shadowing,
permanent purge, and encrypted-at-rest state remain separate work.
