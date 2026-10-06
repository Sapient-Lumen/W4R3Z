# Hostile builders (treat builders as adversaries)

DeriveBSD assumes a builder can be compromised.
The system must remain safe even if a builder tries to:
- exfiltrate secrets
- fetch undeclared inputs
- smuggle unexpected outputs
- claim false provenance

## Baseline stance

- Builders do **not** get secrets.
- Builds run sandboxed (jail on FreeBSD) with **network denied by default**.
- Builders get a **minimal store view**: only declared store objects in the input closure are visible (see `docs/152-store-view-minimization.md`).
- Inputs come only from the Lock/fetch phase and are hash-verified.
- Outputs are accepted only if they match the **expected digests** derived from the Plan.
- Store objects are treated as immutable facts: consume from read-only snapshots/datasets and verify at the edges (see `docs/153-store-immutability-and-toc-tou.md`).

- Builders are **resource-bounded** by policy (CPU/memory/process/IO) to reduce DoS blast radius (see `docs/143-resource-controls-rctl-racct-cpuset.md`).

This makes builders closer to “hostile compilers” than trusted system components.

## What provenance can and cannot do

Signed provenance is still useful, but it is **a claim**.
Policy may require it, but DeriveBSD should not treat it as sufficient.
The hard guarantees come from:
- pinning inputs
- sandbox enforcement
- deterministic hashing
- closure proofs (`docs/90-closure-proof.md`)

## Optional strengthening (policy-controlled)

- multi-builder: require matching outputs from independent builders
- witness rebuilders: require N independent rebuild attestations for promotion (see `docs/116-witness-rebuilders-diffoscope.md`, RFC-0084)
- reproducibility checks: rebuild locally/second-site and compare digests
- transparency logs for public audit (`docs/59-transparency-log-rekor.md`)

Pointers:
- sandbox mechanics: `docs/45-build-sandbox-jails.md`, `docs/49-capsicum-casper-hardening.md`
- provenance formats: `docs/31-provenance-and-sbom.md`, `docs/71-attestations-dsse-in-toto-slsa.md`

Last updated: 2026-02-23
