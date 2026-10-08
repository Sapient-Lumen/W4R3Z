# Rev0866 online research and design implications

Research review date: 2026-07-20. Sources inform architecture and scope; no
citation is treated as proof that AnonSync implements the cited construction or
guarantee. Very recent 2026 preprints are explicitly speculative.

## 1. Making CRDTs Byzantine fault tolerant

Primary source: Martin Kleppmann, “Making CRDTs Byzantine Fault Tolerant,”
PaPoC 2022, ACM DOI 10.1145/3517209.3524042.

https://dl.acm.org/doi/10.1145/3517209.3524042

Design implication: immutable hash-linked operations and deterministic
validation can adapt eventual-consistency designs to a hostile setting, but
Byzantine behavior must be modeled explicitly. Rev0866's evidence/projection
split and retained fork branches align with that direction.

Caution: a content hash is not actor authentication. Rev0866 has no signed
membership or access-control model and therefore does not claim Byzantine fault
tolerance.

## 2. The Blocklace and extend-only directed posets

Primary sources:

- Paulo Sérgio Almeida and Marc Shapiro, “The Blocklace: A Byzantine-repelling
  and Universal Conflict-free Replicated Data Type,” arXiv:2402.08068.
  https://arxiv.org/abs/2402.08068
- Florian Jacob and Hannes Hartenstein, “On Extend-Only Directed Posets and
  Derived Byzantine-Tolerant Replicated Data Types,” arXiv:2304.04318.
  https://arxiv.org/abs/2304.04318

Design implication: an immutable causal graph can expose equivocation and make
application state a deterministic derivation from shared evidence. This
supports retaining nodes separately from active projection and naming exact
predecessors rather than treating a compact vector as proof of possession.

Caution: AnonSync still needs its own authenticated membership, file/tombstone
semantics, bounded dissemination, payload lifecycle, and privacy model.

## 3. Git exact parent identities

Official source: `git-commit-tree` documentation.

https://git-scm.com/docs/git-commit-tree

Design implication: content-addressed objects with exact parent object IDs and a
set of heads are a mature representation of possessed history. They make the
difference between “I summarize this ancestry” and “I have these exact
predecessor objects” concrete.

Caution: Git supplies neither CRDT conflict validity nor actor authorization,
peer quotas, deletion stability, or anonymity.

## 4. Automerge change hashes, dependencies, and queued changes

Official sources:

https://automerge.org/automerge/automerge/struct.AutoCommit.html

https://automerge.org/automerge/src/automerge/read.rs.html

Design implication: SHA-256 change identity, dependency hashes, complete
history, and queuing changes until causal dependencies are available are
practical production CRDT patterns. Rev0866's pending state and evidence-complete
anti-entropy follow the same broad evidence-before-application principle.

Caution: AnonSync's canonical bytes, single-writer actor epochs, fork quarantine,
file preservation policy, and future trust state are distinct design choices.

## 5. SQLite atomic commit, WAL, and the 2026 WAL-reset bug

Official sources:

https://www.sqlite.org/atomiccommit.html

https://sqlite.org/wal.html

https://sqlite.org/releaselog/3_51_3.html

SQLite documents WAL's transaction/checkpoint model and records a rare
WAL-reset data race affecting versions 3.7.0 through 3.51.2. It was fixed in
3.51.3 on 2026-03-13. The AnonSync cube bundles SQLite 3.53.3 with source ID
`2026-06-26 20:14:12 d4c0e51e...`, so the checked-in amalgamation is newer than
the fix.

Design implication: the next operation vertical slice can and should bind dot
reservation, exact envelope bytes, parent edges, head replacement, and outbox
intent in one SQLite transaction. The runtime must assert the linked SQLite
source/version, keep WAL sidecars with the database, document synchronous and
checkpoint policy, bound WAL growth, and crash-test ambiguous commit outcomes.

Caution: merely bundling a fixed version does not prove correct VFS behavior,
fsync durability, multi-connection scheduling, checkpoint policy, or product
transaction composition.

## 6. Composable deterministic reconstruction

Very recent source: “A Composable CRDT Layer for Byzantine-Resilient
Deterministic Reconstruction,” arXiv:2606.18966.

https://arxiv.org/abs/2606.18966

Design implication: separating converged evidence from pure deterministic state
reconstruction is closely aligned with the architecture found necessary in this
audit.

Caution: this June 2026 preprint is a research lead, not settled implementation
authority. Rev0866 implements a narrow in-memory file-operation oracle, not the
paper's full construction.

## 7. Decoupled and replicated trust state

Very recent sources:

- “Decoupling Trust in Byzantine CRDTs: Fine-grained Post-Compromise Handling
  without Breaking Causality,” arXiv:2606.31759.
  https://arxiv.org/abs/2606.31759
- “A Dual-CRDT Architecture for Decentralized Trust Governance and Evolution,”
  arXiv:2607.06068.
  https://arxiv.org/abs/2607.06068

Design implication: retained evidence and trust decisions may need separate
replicated state so compromise, revocation, and recovery can reclassify
application evidence deterministically without rewriting history.

Caution: both are very recent. Trust-state convergence, authorization policy,
recovery, and malicious-governance resistance remain open AnonSync design work.

## 8. Evidence projection for non-associative state

Very recent source: “Byzantine Accountability Without Consensus: Strong
Eventual Consistency for Non-Associative, Stochastic, Robust Aggregation.”

https://arxiv.org/html/2607.10305v1

Design implication: a converged evidence product plus deterministic pure
projection is useful even when application combination is not a simple
associative merge. That reinforces treating `SyncReplicaEvidenceProjection` as
a reference owner rather than burying validity in arrival-time mutation.

Caution: this is a July 2026 research lead and does not establish AnonSync's
security, accountability, or convergence.

## 9. Memory-exhaustion attacks on retained causal graphs

Very recent source: “Memory-Exhaustion Attack on the Blocklace
Byzantine-Repelling Conflict-Free Replicated Data Type,” arXiv:2607.15185.

https://arxiv.org/abs/2607.15185

Design implication: convergence and equivocation exposure do not make unbounded
retention safe. Authenticated members can still be resource adversaries.
Production admission needs hard envelope, parent-fan-in, unresolved-dependency,
per-peer memory, disk, traversal-work, retry-lifetime, and bandwidth limits,
plus a policy for evidence that is valid but over quota.

Caution: this July 2026 preprint is speculative pressure, not a complete defense
or proof that Rev0866's in-memory caps solve storage denial of service.

## Synthesis for AnonSync

The converging architectural direction is:

1. freeze one canonical update and bind its exact immediate predecessors;
2. authenticate actor/key and membership epochs independently of content hash;
3. retain immutable evidence separately from active and visible projections;
4. derive validity deterministically from evidence plus trust state;
5. persist local identity, graph mutation, and dissemination intent at one
   recoverable transaction cutpoint;
6. exchange graph heads and missing dependencies under strict amplification and
   storage budgets;
7. keep a pure global projector as the differential oracle for an incremental
   implementation; and
8. treat privacy as a separate threat-model-driven layer rather than an implied
   property of peer-to-peer transport.

Rev0866 materially supplies items 1, 3, part of 4, and a bounded in-memory test
oracle for item 7. The production SQLite/wire/payload vertical slice, actor and
membership authority, stable compaction, resource governance, and anonymity
remain missing.
