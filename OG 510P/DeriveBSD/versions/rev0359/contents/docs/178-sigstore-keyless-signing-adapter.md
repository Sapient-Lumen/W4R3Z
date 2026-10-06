# Sigstore keyless signing adapter (optional)

DeriveBSD already uses:
- DSSE/in-toto attestations (`docs/71-attestations-dsse-in-toto-slsa.md`)
- optional transparency lanes (Sigsum, SCITT) (`docs/131-*`, `docs/132-*`)
- optional OCI transport (`docs/74-oci-transport-and-layering.md`, `docs/133-bootable-oci-host-images-bootc-lessons.md`)

A practical ecosystem feature for day-1 adoption is an adapter for **Sigstore/Cosign**:
- keyless signing (OIDC identity → short-lived cert)
- storing signatures/attestations in OCI registries

This is an adapter lane: DeriveBSD remains the authority about what is valid; Sigstore is a distribution and UX bridge.

See RFC-0113.

## Why this is “juicy”

Key management is a deployment killer.
Sigstore’s keyless flow can lower the barrier for:
- signing dev artifacts
- publishing attestations
- integrating with existing OCI registries

## DeriveBSD mapping

### 1) Treat sigstore bundles as evidence
Introduce an optional evidence object:
- `sigstore.bundle` (references artifact digest + includes cert chain + Rekor inclusion proof if used)

Policy decides:
- whether sigstore evidence is accepted
- which identity issuers are allowed
- whether transparency proof is mandatory

### 2) Keep DeriveBSD’s verification as the source of truth
Even if artifacts move through an OCI registry:
- DeriveBSD still verifies artifact digests and closure proofs
- sigstore evidence is *additional*, not a replacement

### 3) Avoid coupling to public infrastructure
Support both:
- public sigstore (Fulcio/Rekor)
- private deployments (custom roots/logs)

## Non-goals

- replacing DeriveBSD trust policy with “whatever cosign verifies”
- requiring OIDC connectivity for offline/air-gapped channels

Last updated: 2026-02-24
