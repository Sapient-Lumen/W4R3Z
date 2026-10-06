# RFC-0034: Trust policy schema (namespaces, channels, keys)

- Status: draft
- Created: 2026-02-23

## Problem

Verification is only as good as the trust configuration.
If trust policy is implicit, ad-hoc, or embedded in code:

- audits become guesswork
- policy changes are hard to diff/review
- multiple verifiers drift (inconsistent acceptance)

We need a minimal, typed data schema for trust.

## Proposal

Introduce a `trust-policy` object (JSON, JCS-canonicalizable) that binds:

- **namespaces** (tenant / org / repo root)
- **channels** (optional constraints like rollback window and expiry requirement)
- **keys** with roles (root/signing/policy) and validity windows
- **per-target acceptance rules** (host/microvm): required signers, required attestation identifiers, require closure proof

Schema + example:

- `spec/trust.policy.schema.json`
- `spec/examples/trust.policy.json`

## Notes

- v0.1 intentionally avoids specifying key encodings and signature formats; those are policy-defined.
- policy decision records may be signed by `policy` keys, while artifacts/closure proofs are signed by `signing` keys.

Pointers:
- `docs/57-namespaces-channels-trust.md`
- `docs/61-channel-metadata-tuf-inspired.md`
- `adrs/ADR-0009-artifact-verification.md`
