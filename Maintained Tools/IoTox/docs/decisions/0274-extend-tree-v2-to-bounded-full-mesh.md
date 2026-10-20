# ADR 0274: Extend tree-v2 automation to a bounded full mesh

Date: 2026-08-31

Status: accepted

## Context

ADR 0273 deliberately activated only one automatically selected remote writer. The underlying
tree-v2 branch, causal merge, conflict, tombstone, graph-transfer, and authorization formats were
already bounded multi-writer constructions. A third writer therefore did not require new peer
framing, but the local signed automation record could represent only one remote stable principal and
`sync-share ... read-write` refused replacement.

A naive extension would introduce two failure modes. First, one offline peer could repeatedly drive
namespace-wide exponential backoff and delay every healthy peer. Second, appending authority before
checking local vector and tree-wire capacity could leave a durable grant that the requested local
automation could never represent.

## Decision

Freeze the local automation-v2 record in `../protocol-sync-automation-v2.md`. It stores a sorted,
unique set of at most 15 remote stable principals in a fixed 4,808-byte device-signed record. Legacy
v1 records remain readable and exact duplicate writes remain v1; an explicit change migrates to v2
at the next generation. No peer frame or feature bit changes.

Make read-write sharing additive. Each bilateral ceremony still requires the local RecallRoot and a
currently transcript-proven exact-v3 peer. Prepare and commit preflight both the 16-writer tree-v2
inventory limit and the 15-remote automation limit before accepting a new signed grant. Exact shares
are idempotent. There is no transitive group authority or remote path selection.

Retain one in-flight periodic action per writable namespace, but keep due time and consecutive
failures independently for every remote principal. A deterministic round-robin cursor selects among
due sources. An unavailable source backs off alone; healthy sources continue at their own interval.
Local writable reconciliation still precedes every remote pull.

The acceptance sequence is:

1. byte-level v2 codec/store tests, canonical-order and duplicate refusal, v1 verification, exact-v1
   duplicate stability, and explicit v1-to-v2 migration;
2. deterministic per-peer fairness/backoff tests;
3. local three-writer merge across all six arrival orders with identical projection and conflict
   provenance;
4. three genuine source-linked IoTox daemons, one private c-toxcore bootstrap, all three friendship
   edges, all six directional shares, three concurrent offline values, exactly two alternatives per
   node, and one later explicit causal resolution;
5. the same process inside one networkless Sandwurm/KVM guest, with only content-free evidence
   exported.

## Consequences

Three or more owners can now build an explicit bounded read-write full mesh using only the existing
ordinary commands. The local writer plus 15 remote writers is a protocol ceiling, not a recommended
fleet size. Setup grows quadratically, conflict probability rises with active writers, and every
node must explicitly authorize every writer whose branch it accepts.

The data model does not silently lose concurrent values: three unequal offline edits yield one
deterministic ordinary projection plus two provenance-bearing alternatives at every converged node.
A later edit resolves them only after its writer has observed all competing frontiers.

This decision does not add group invitation UX, transitive membership, partial-mesh routing,
filesystem watching, incremental projection, tree-v2 range/auxiliary-lane transfer, recoverable GC,
retention/archive policy, revoked-writer cutoff, malicious-fork or conflict-storm bounds,
independent-machine evidence, or a sole-copy recommendation. Those remain roadmap work.
