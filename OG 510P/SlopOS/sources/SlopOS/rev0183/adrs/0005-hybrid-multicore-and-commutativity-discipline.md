# ADR-0005: Adopt Hybrid multicore + interface-first commutativity discipline

Decision node(s): D-MK, D-COMMUTE, D-CONC

## Context
We cannot defer multicore verification and we do not want to ship an architecture that is intrinsically limited to closely-coupled SMP.
At the same time, a pure multikernel approach shifts much of the complexity into replication/protocol reasoning, which can be a large proof and engineering surface.

We also want all four product shapes (workstation, cloud substrate, embedded/appliance, agent/automation) to remain viable without forks.
That requires an architecture that:
- scales across NUMA/chiplets without assuming a global serialization point;
- still allows a practical, verifiable in-cluster baseline;
- keeps high-frequency privileged actions scalable by making coordination requirements explicit in the *interface/spec*, not hidden in implementation.

## Decision
We adopt the following direction as the default interpretation of D-MK and D-COMMUTE:

1) **Hybrid multicore (D-MK)** is the intended endgame:
   - **Across clusters** (NUMA nodes / sockets / chiplets / topology-defined regions), use multikernel-style ownership and explicit messaging.
   - **Within a cluster**, use SMP as a local optimization.
     - Early profiles may use a big-kernel-lock SMP baseline for verification speed, but must still preserve explicit ownership boundaries so we can evolve toward sharded/replicated in-cluster structures.

2) **Interface-first scalability (D-COMMUTE)** is a required discipline:
   - For privileged action families, prefer specs where the common-case operations commute under explicit preconditions.
   - Where operations are **non-commutative**, we must name the minimal serialization boundary (see `hot-action-boundaries-v0.md`) and treat it as a first-class performance and proof target.

This decision does **not** pick the final replication strength or fault model; those remain explicit follow-ups. Cluster derivation is pinned as an auditable artifact surface (`cluster-derivation.md` → CH-CLUSTERMAP v0) and can evolve by versioned schema/policy rather than ad-hoc implementation drift.

## Interfaces / schemas impacted
- IF-KABI (privileged action dispatch) + CH-KABI v0: action families must declare conflict keys and commutativity stance.
- CH-HWFACT v0 (and D-SKB): topology facts must be available for cluster placement decisions.
- CH-CLUSTERMAP v0: derived cluster partition artifact bound to CH-HWFACT (+ optional policy digest).
- CH-LOG / receipts: log append/export must avoid introducing an accidental global serialization point.

## Consequences
Positive:
- Keeps the many-core/NUMA direction viable without forcing a “distributed-kernel everywhere” proof story on day 1.
- Gives a concrete contract for scalability: coordination is demanded by the spec only when unavoidable.
- Aligns all four product shapes by making topology and coordination costs explicit and reviewable.

Negative / costs:
- Requires two regimes of reasoning (in-cluster SMP + cross-cluster messaging) and careful boundary hygiene.
- Forces discipline in interface design: making order non-observable when unnecessary can be tedious and may constrain some legacy compatibility strategies.

Follow-ups (explicitly tracked):
- Tighten the CH-HWFACT `cpu_topology` surface (e.g., cache-group/NUMA fidelity) only when needed, and keep it bounded.
- Decide the minimum replication/consistency contracts for cross-cluster metadata.
- Extend the hot-action surface beyond v0 only when there is evidence and a clear commutativity/serialization stance.

## Evidence
- Multikernel model motivation: locality and explicit message structure on many-core/heterogeneous hardware (REF-MULTIKERNEL-SOSP09).
- Hybrid stance: multikernel notes local shared-memory as an optimization while keeping global message structure (REF-MULTIKERNEL-SOSP09).
- Commutativity discipline: scalable commutativity rule and its verified proof (REF-SCR-TOCS15).
- Archive wiring that makes this enforceable:
  - `docs/30-architecture/commutativity-and-interface-scalability.md`
  - `docs/30-architecture/hot-action-surface-v0.md`
  - `docs/30-architecture/hot-action-boundaries-v0.md`

## Affected registries
- Proof obligations: PO-COMMUTE-SPEC, PO-COMMUTE-TEST, and the v0 hot-action POs.
