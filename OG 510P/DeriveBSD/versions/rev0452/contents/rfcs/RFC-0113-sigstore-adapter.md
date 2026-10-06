# RFC-0113: Sigstore/Cosign keyless signing adapter (optional)

Status: **draft**

## Problem

DeriveBSD defines a strong verification model, but ecosystem adoption benefits from:
- ergonomic signing workflows
- OCI registry-native signature/attestation distribution
- identity-based signing that reduces key handling

Sigstore/Cosign is widely used for these workflows.

## Goals

- Allow sigstore artifacts (signatures/attestations) to be consumed as **evidence objects**.
- Keep DeriveBSD’s trust policy the source of truth.
- Support both public and private sigstore deployments.

## Proposal

### Evidence object: `sigstore.bundle`
A content-addressed object that contains or references:
- artifact digest / subject
- signing identity (certificate subject / OIDC issuer)
- signature material
- optional transparency proof(s)

### Verification
Policy-controlled checks:
- identity allowlist (issuer, subject, SANs)
- certificate chain validation
- transparency inclusion (if required)
- binding to the exact artifact digest

### Integration points
- OCI transport lane (`docs/74-*`, `docs/133-*`)
- attestation lane (`docs/71-*`)
- transparency lanes (`docs/131-*`, `docs/132-*`)

## Tradeoffs

- Adds another signature ecosystem to support.
- Must avoid letting “keyless by default” become “trust anything by default”.

