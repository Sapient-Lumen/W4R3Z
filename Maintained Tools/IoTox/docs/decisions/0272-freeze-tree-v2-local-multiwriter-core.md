# ADR 0272: Freeze the tree-v2 local multiwriter core

Status: accepted local construction, 2026-08-31

## Context

ADR 0271 refused to create a read-write share by granting two capabilities over the existing linear
signed HEAD. That refusal was necessary: receipt order is not edit causality, a whole-tree archive
cannot transfer one changed file efficiently, and last-writer-wins would silently discard offline
work. The next implementation boundary must establish convergence and local crash truth before a
peer feature is advertised.

The critical distinction is between a branch the daemon has received and a branch the user has
actually seen in the writable directory. Treating both as "observed" makes a local edit performed
against an older visible tree dominate a newly received remote edit. That is wall-clock/reconnect
ordering disguised as causality.

## Decision

Reserve namespace engine 4 as `tree-v2` and freeze these local formats and rules:

1. `IOTXTVM1` is a canonical signed-branch manifest over per-file SHA-256 CAS objects. Directory,
   file, and tombstone entries carry an origin stable writer and branch generation. One path may
   retain multiple concurrent origins.
2. `IOTXTVB1` is one independently monotonic Ed25519-signed branch per authorized stable writer. A
   branch names its exact predecessor and a sorted vector of exact signed branch-record observations.
   Wall clocks do not participate.
3. Immutable branch records and manifests commit before the writer-specific current pointer. Every
   observation must resolve to its exact retained signed record. A carried foreign value must already
   occur in an authenticated visible/current proof; annotating bytes with another writer's key is not
   provenance.
4. A value is dominated only by a branch that causally observes its origin and replaces it. Omission
   of an unseen value is not deletion. Equivalent concurrent payloads coalesce deterministically;
   unequal candidates remain a conflict.
5. Deletion is a signed tombstone event. A concurrent live edit beats a tombstone only in the ordinary
   projection; the tombstone remains under conflict provenance. Nothing in this ADR purges history or
   defines delete-everywhere.
6. The deterministic ordinary projection chooses directory before file before tombstone, then the
   canonical origin order. Every unselected candidate is materialized below
   `.iotox-conflicts/by-origin/WRITER/GENERATION/KIND/PATH`. A live value is never silently discarded.
7. A complete target tree is built beside the writable directory and switched with Linux
   `renameat2(RENAME_EXCHANGE)`. The source is hashed against the exact scan result before and after
   target construction. The old tree is removed only after the new projection and its manifest marker
   revalidate.
8. `IOTXTWS1` is stable-device-signed local workspace truth. It binds the canonical path, active
   manifest, and—most importantly—the exact signed branch frontier that was actually projected. A
   pending state additionally binds the scanned worktree manifest, target manifest, and target
   frontier before exchange. Recovery distinguishes pre-exchange and post-exchange trees by their
   exact projection marker and refuses ambiguity.
9. One reconciliation cycle scans against the active visible frontier, commits new CAS objects,
   publishes the local edit branch without observing newly received invisible branches, publishes a
   second causal merge branch that retains every concurrent value, journals the projection, exchanges
   it, and finishes the workspace checkpoint.

The local branch store rejects same-writer forks, stale/gapped advances, invented observation records,
forged carried values, silent observed-value drops, unsafe paths, linked/public state, and quota
overflow. Parent directories must exist as live manifest entries. The object store uses no-replace
digest identity and verifies the complete source before and after copy.

## Not yet activated

No peer feature bit, peer frame, Agent service, automation mode, `sync-create ... read-write`, or
`sync-share ... read-write` behavior is enabled by this ADR. The next ordered gates are:

1. bounded inventory, immutable-record, manifest, and file-object transfer framing;
2. authority-gated publisher/subscriber state machines with durable receive attempts;
3. recipient-local invitation/policy installation and read-write grant ceremonies;
4. periodic Agent reconciliation and content-free status;
5. history/conflict/tombstone reachability plus recoverable GC;
6. revoked-writer/offline-branch policy; and
7. deterministic crash-edge, conflict-storm, malicious-peer, and two-guest Sandwurm qualification.

Until those pass, `tree-v2` is a tested local construction boundary, not an operator-visible
bidirectional sync claim.

ADR 0273 subsequently activates the bounded pairwise peer and command surface. The list above
remains the historical boundary of this decision; GC, revoked-writer policy, conflict-storm bounds,
and broader qualification remain open under the follow-up.

## Consequences

IoTox now has a real convergence model rather than a renamed linear publisher. Offline edits survive
reconnect in either receive order, deletion-versus-edit retains both outcomes, and a later ordinary
edit resolves the displayed conflict causally. This costs metadata and may perform a full local tree
projection exchange even though network/storage objects are per-file. Projection optimization,
metadata preservation beyond the executable bit, archive/restore, ignores, case-folding portability,
and cross-filesystem worktrees remain explicit future work.
