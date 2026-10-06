# Runtime blast-radius contract (microVM-first)

DeriveBSD’s runtime is designed to minimize “what can go wrong” if a workload is malicious or compromised.

This file defines the **default invariants** for microVM launches and the **explicit opt-ins** that increase authority.
The contract is enforced by:
- planning (policy denies invalid manifests)
- runtime (`derive-vmmd`) hard checks
- host primitives (pf anchors, rctl/cpuset, devfs rulesets, ZFS datasets)

Review workflow note: authority changes should be surfaced via blast-radius diffs (`docs/106-blast-radius-diff.md`).

## Defaults (v1)

### Authority
- microVM processes run under a dedicated, unprivileged service account
- no host filesystem passthrough
- no device passthrough

### Storage
- base image/root dataset is **read-only**
- writable state is **ephemeral by default**
- persistent overlays require an explicit dataset reference and policy allow

### Network
- networking is denied unless explicitly declared
- all allowed networking is mediated by host pf rules via a **per-instance anchor**
- default mode is `isolated` or `nat` (policy-defined), never `bridged`

### Secrets
- secrets are **not baked** into images
- secrets are injected via a dedicated channel (virtio-console or backend equivalent)
- secrets names are part of the manifest contract and are policy-enforceable

### Resources
- every instance is assigned:
  - CPU/memory ceilings
  - I/O limits where supported
- host enforces ceilings using OS primitives (rctl/cpuset) rather than trusting in-guest limits

## Opt-ins (must be policy-gated)

These raise blast radius and must be explicit in the runtime manifest and accepted by policy:

- `bridged` networking
- persistent overlays / writable root
- any passthrough device
- high resource ceilings (large RAM, many vCPUs)
- privileged injection channels

## What gets bound to the derivation

A runtime launch must bind back to:
- `artifact_digest` (what will run)
- `runtime_manifest_digest` (how it will run)
- `policy_decision_digest` (why it’s allowed)
- `closure_manifest_digest` (what else must exist)

These bindings support:
- “why/what/where-from” explanations
- offline verification
- safe rollbacks

## Enforcement sketch (v1)

At launch time `derive-vmmd` must:
1. Verify digests/signatures/attestations required by policy.
2. Verify a closure proof exists for the chosen artifact/manifest pair.
3. Apply the per-instance pf anchor ruleset.
4. Apply rctl/cpuset ceilings.
5. Refuse any manifest fields that are not explicitly supported (no silent ignore).

Pointers:
- pf anchors: `docs/67-pf-anchors-per-instance.md`
- resource profiles: `docs/68-resource-profiles-rctl-cpuset.md`
- runtime manifest: `docs/33-runtime-manifest-schema.md`
- closure proofs: `docs/90-closure-proof.md`
- policy decision records: `docs/93-policy-decision-records.md`

Last updated: 2026-02-23
