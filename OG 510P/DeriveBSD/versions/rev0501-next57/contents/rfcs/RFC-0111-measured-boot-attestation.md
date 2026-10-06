# RFC-0111: Measured boot + remote attestation lane (optional)

Status: **draft**

## Problem

DeriveBSD can verify artifacts, closure proofs, and policy decisions — but it still needs an answer to:

> *Which* host ran *which* artifact, and can we prove the host booted into the expected generation?

Without measured boot, a compromised boot chain can:
- run an older/vulnerable generation while claiming to be current (rollback-by-compromise)
- exfiltrate secrets before DeriveBSD’s higher-level policy is even active

## Goals

1) Define **standard evidence objects** that bind platform state to DeriveBSD deployment objects.
2) Keep the feature **optional**, enabled only when policy requires it.
3) Avoid “golden PCR value” brittleness by preferring event-log-aware verification.

## Non-goals

- Mandatory TPM / measured boot for DeriveBSD v1.
- Full runtime integrity monitoring pipeline.

## Prior art / terminology

Adopt the IETF RATS conceptual model:
- Attester, Verifier, Relying Party
- Evidence, Endorsements

See: RFC 9334 (RATS Architecture).

## Proposed evidence objects

### A) `boot.manifest` (new)
A content-addressed object emitted at plan/activation time that enumerates boot-critical components for a deployment:
- loader components
- kernel + modules bundle digests
- activation binary digest
- cmdline profile digest

The manifest’s digest is referenced by the deployment ref.

### B) `boot.attestation` (new)
A content-addressed object with a canonical JSON form, signed by the host attestation key.

Fields (v0 sketch):
- subject: deployment ref digest + boot.manifest digest
- attester: host identity key id (from trust bootstrap)
- tpm: pcr_bank + pcr list + quote + eventlog digest
- time: optional trustworthy time evidence pointer

Schema: `spec/boot.attestation.schema.json`.

### C) `attestation.receipt` (optional)
A verifier-issued statement:
- references a specific `boot.attestation` digest
- references the policy snapshot digest used to evaluate it
- includes pass/fail + reason codes

This is intentionally analogous to policy decision records.

## Verification philosophy

### 1) Prefer event-log-based verification
PCR values alone are opaque.
Verification SHOULD use the measured boot event log to reconstruct expected PCR extensions,
and compare the result to the quoted PCRs.

### 2) Bind the boot chain to DeriveBSD deployment objects
The verifier should check that event log entries correspond to the expected `boot.manifest` components.

### 3) Make policy explicit
Policies SHOULD express what is required:
- which PCRs/banks
- which signing keys
- whether receipts are required for promotion/activation

## Integration points

- `docs/70-tpm-and-host-identity.md`: host identity + sealed secrets
- `docs/51-secure-boot-integration.md`: boot chain binding
- `docs/112-health-gated-updates.md`: advance rollback indices only after health success; optionally require attestation receipt
- `docs/93-policy-decision-records.md`: reuse the “receipt as evidence” pattern

## Tradeoffs

- Adds operational complexity (key enrollment, verifier infrastructure).
- Requires careful UX to avoid turning “optional” into “everyone does it wrong.”

