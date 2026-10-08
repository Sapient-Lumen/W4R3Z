# Next work after AnonSync rev0868

## Highest-leverage vertical slice

Implement one SQLite-backed replica-operation owner for a single folder. The
transaction should atomically own:

- durable local dot/counter reservation;
- exact canonical authenticated operation bytes;
- exact parent edges;
- exact deterministic resource charges;
- retained evidence state;
- deterministic projection and causal-head changes; and
- sender outbox intent.

Remote admission should preserve four orthogonal outcomes across crash:
canonical validity, authenticated trust/admission, graph applicability, and
local retention availability. `CapacityBlocked` must not erase sender ownership
or create receiver quarantine.

## Required crash and retry tests

Add crash-frontier probes around:

1. local counter reservation before/after operation publication;
2. operation and parent insertion before/after projection/head update;
3. outbox insertion before/after commit;
4. remote admit versus blocked verdict;
5. acknowledgement before/after sender outbox retirement;
6. restart and complete revalidation/reprojection; and
7. quota/policy generation changes that wake blocked retry.

The test should use two actual processes and the bundled SQLite owner rather
than only the in-memory network simulator.

## Security and fairness

Before arbitrary peers can reach the vertical slice:

- bind operations to authenticated actor and membership/key epochs;
- define rotation, revocation, recovery, and old-epoch rejection;
- enforce cheap pre-authentication limits;
- add per-principal and per-folder quotas with reserved recovery capacity;
- bound missing-dependency requests, retry metadata, CPU, bytes, and time; and
- make operator policy and pressure state observable without turning them into
  canonical evidence.

## Retention lifecycle

Design checkpoint/stability evidence that can justify compaction without
silently accepting old resurrected history. Separate immutable identity proof,
hot dependency-service bytes, rebuildable projection indexes, payload chunks,
and compact fork/revocation proofs. Define old-replica rejoin explicitly.

## Anti-entropy

Replace full retained-set replay with authenticated head/root summaries and
bounded exact-ID reconciliation. Summaries remain acceleration; exact canonical
nodes and parents remain authority. Differentially test any incremental
projector and reconciliation layer against the current global oracle.

## Resource measurement

Measure and bound actual RSS, allocator overhead, SQLite pages/WAL/snapshot,
filesystem blocks, payload staging, wire bytes, CPU, and wall time under:

duplicate replay, capacity block, malformed envelopes, fork floods,
missing-parent chains, wide fan-in, and fresh authenticated/unauthenticated
identities.

## Privacy

Write a threat model before exposing detailed pressure vectors. Evaluate load
leakage, retry-timing linkability, membership/activity inference, path/dependency
shape, padding, coarsening, session binding, rate limiting, forward secrecy, and
post-compromise behavior.
