# Research notes reviewed for rev0867

Reviewed 2026-07-21. These sources inform design direction; none is treated as
proof that AnonSync already has the described properties.

## CRDT foundations and deltas

- Nuno Preguiça, Carlos Baquero, Marc Shapiro, *Conflict-free Replicated Data
  Types: An Overview*, arXiv:2310.18220 — broad CRDT semantics, convergence
  conditions, and design taxonomy. https://arxiv.org/abs/2310.18220
- Paulo Sérgio Almeida, Ali Shoker, Carlos Baquero, *Delta State Replicated Data
  Types*, arXiv:1603.01529 — motivates dissemination of joinable deltas instead
  of complete state, while preserving state-based reasoning.
  https://arxiv.org/abs/1603.01529

Inference for AnonSync: retain a simple complete-evidence oracle for differential
checking, but do not make full-history exchange or whole-graph reprojection the
production scaling path.

## Byzantine evidence and authenticated causality

- Martin Kleppmann, Heidi Howard, *Byzantine Eventual Consistency and the
  Fundamental Limits of Peer-to-Peer Databases*, PaPoC 2022 — explains why
  signed immutable operations and explicit causal dependencies can make some
  Byzantine behavior detectable, and where equivocation limits remain.
  https://martin.kleppmann.com/papers/bft-crdt-papoc22.pdf
- Paulo Sérgio Almeida et al., *Blocklace: Byzantine Fault-Tolerant Conflict-free
  Replicated Data Types*, arXiv:2402.08068 — explores hash-linked partially
  ordered blocks as a basis for Byzantine-tolerant replicated structures.
  https://arxiv.org/abs/2402.08068

Inference for AnonSync: exact parent IDs and canonical hashes are useful evidence
plumbing, but authorization still needs signatures, membership, key/epoch
lifecycle, revocation, and durable anti-rollback state.

## Memory-exhaustion pressure

- *Memory-Exhaustion Attack against Byzantine-Tolerant CRDTs*,
  arXiv:2607.15185, submitted 2026-07-16 — a very recent preprint warning that
  finite eventual harm can still be made arbitrarily large when replicas eagerly
  retain evidence from fresh identities; it discusses limiting identities and
  interest-driven replication. https://arxiv.org/abs/2607.15185

This preprint is a warning and speculative lead, not settled authority. Its
threat model directly reinforces the limit of rev0867: a global aggregate budget
prevents unbounded local retention but does not provide fairness, Sybil
resistance, or a safe garbage-collection rule. Authentication-scoped quotas and
bounded unknown-identity discovery should precede broad peer admission.
