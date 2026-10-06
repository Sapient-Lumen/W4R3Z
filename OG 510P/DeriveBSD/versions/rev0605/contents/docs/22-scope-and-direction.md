# Scope and direction

**Single direction (v0):** DeriveBSD, **FreeBSD-first**, **hypervisor-centric** runtime.

**Mission kernel:** compile declarative intent into verified, rollbackable FreeBSD system and workload artifacts, and make every privileged transition least-authority, explainable, and receipt-producing. The first product is profile A: a small fleet host/control plane, not a simultaneous workstation, general-purpose OS, and appliance platform.

There are no “alternate host OS” pathways in scope (no alternate host OS targets, no portability hedging).

## Why this scope exists

DeriveBSD’s core bet is that FreeBSD’s primitives (jails, ZFS boot environments, pf anchors, Capsicum/Casper) compose cleanly with a Derive-style pipeline:

- Spec → Lock → Plan → Artifact
- stable sandbox + trust model
- bounded activation + rollback story

Scope control prevents “monster growth” by forcing every new idea to attach to those invariants.

See also: v0 cutline + feature tiers (`docs/401-v0-cutline-and-feature-tiers.md`).

## Active v0 deliverables

- Store + sandbox + cache trust (signed)
- System generations + ZFS boot environment activation
- MicroVM artifact target (bhyve-first)
- VM control plane (`derive-vmmd`) with least privilege
- Standard config + secrets injection contracts
- pf-composed virtual networking
- Provenance attestations + optional SBOM emission
- **Developer UX parity:** reproducible, fast `derive develop` / `derive shell` environments

Last updated: 2026-06-18r616
