# P2P distribution + swarm caches (Dragonfly lesson)

At fleet scale, “one origin + many pullers” collapses.
Even with HTTP caches, large rollouts create hotspots and long tail latency.

Container ecosystems built P2P distribution layers (notably CNCF Dragonfly) to turn each node into a
**verified partial mirror**.

DeriveBSD can steal the shape while keeping our core invariants:
- bytes are always verified against signed manifests
- transports are optional and policy-bound
- peers are never trusted principals

## Prior art

- **Dragonfly (d7y)**: P2P-based file and image distribution and acceleration; integrates with OCI registries and can
  accelerate on-demand filesystem formats (e.g., Nydus).

Key lesson: “distribution” is a control plane problem (cohorting, scheduling, locality), not just a protocol.

## DeriveBSD direction

### A) Treat P2P as a transport adapter

We already have the concept of **transport lanes** (`spec/transport.policy.schema.json`).
A P2P adapter fits as another method for retrieving blobs/chunks *by digest*.

- Inputs: artifact digest + signed manifest
- Retrieval: ask swarm for chunks; fall back to HTTP if needed
- Verification: always verify chunk digests before use

### B) Keep the P2P service out of the host TCB

Run the swarm agent as a compartmented service (jail/microVM) with:
- scoped network access
- explicit cache directories
- signed config + receipts

Treat it like a “fetch broker”, not a kernel module.

### C) Make poisoning and privacy risks explicit

**Poisoning risk**
- peers may send garbage or attempt downgrade attacks
- mitigations: digest verification, anti-rollback metadata, and receipts

**Privacy risk**
- P2P can leak what you’re pulling (workload identity, access patterns)
- mitigations: restrict to trusted network domains, allow policy to force prefetch/materialize,
  and avoid exporting detailed fetch telemetry by default

### D) Wire into lazy rootfs mounts (optional synergy)

P2P is especially valuable when combined with lazy-mount formats:
- page faults fetch small, random ranges
- swarm locality reduces tail latency

This is optional and should be policy gated.

## Why bake this in early?

If we don’t provide a sanctioned lane:
- operators will deploy third-party P2P daemons without evidence/receipts
- teams will bypass policy to “just speed up pulls”

Greenfield advantage: make the fast path the safe path.

## See also

- Verified lazy rootfs mounts: `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`
- Store/image distribution adapters: `docs/119-casync-cvmfs-distribution.md`
- Anti-rollback / rollback-index lanes: `docs/62-replay-rollback-freeze.md`, `docs/137-anti-rollback-rollback-index.md`
- Transport policy: `spec/transport.policy.schema.json`

Last updated: 2026-02-26
