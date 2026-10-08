# Rev0864 next work

## Product-critical sequence

1. Build a pure C++ replica state/operation model and deterministic network
   simulator with duplication, loss, reorder, partition, heal, crash, restart,
   and eventual-delivery assertions. Make the claimed convergence property
   executable before adding more transport machinery.
2. Bind those operations to a stable canonical protocol envelope and the
   existing durable ingress store. Compare recovered durable state with the pure
   model after every simulated cut.
3. Add a two-process IPv6/IPv4 TCP vertical slice with explicit deadlines,
   mutual TLS 1.3 pinned test identities, protocol-version negotiation, a
   transcript-bound connection capability, reconnect, and replay-safe durable
   application of one operation.
4. Publish an adversary and leakage matrix for payloads, names, sizes, timing,
   membership, topology, IP location, local compromise, stolen devices,
   malicious peers, and relay visibility. Define enrollment, rotation,
   revocation, and recovery before claiming anonymity.

## Parallel correctness debt

5. Audit semantic `*_checked`, `*_verified`, `*_authorized`, and `*_durable`
   booleans. Replace high-authority booleans with state-specific or move-only
   result types where practical.
6. Move build-graph assertions from regex/source scraping toward CMake file API,
   Ninja command graphs, or `compile_commands.json`; reserve lexical audits for
   literal inventory properties.
7. Introduce typed clock/epoch sources and reduce correctness-sensitive ambient
   `uint64_t` epoch inputs.
8. Prototype disposable hostile-SQLite/document workers with sealed descriptors,
   parent-enforced CPU/memory/output/wall limits, and process disposal.
9. Split the public header and the largest orchestration translation units by
   stable domain ownership.
10. Design content-addressed historical evidence and signed SLSA/in-toto-style
    attestations so source archives do not repeatedly embed every old log.
