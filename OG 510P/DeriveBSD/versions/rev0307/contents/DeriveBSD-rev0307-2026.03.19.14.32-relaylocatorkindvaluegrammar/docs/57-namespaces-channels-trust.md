# Namespaces, channels, and trust policy

Trust is policy-defined:
- which namespaces are allowed
- which keys are trusted for which targets
- which attestations are required

Channels select curated streams (stable/beta/nightly) via metadata.

## Trust policy as data

DeriveBSD treats trust policy as a **typed, versioned data object** so that verifiers can be:
- deterministic
- auditable
- diffable in review

Schema + example:
- `spec/trust.policy.schema.json`
- `spec/examples/trust.policy.json`

At minimum, a trust policy binds:
- namespace identifiers
- trusted keys (by role and/or key id)
- per-target requirements (signatures, required attestation identifiers, closure proof requirement)

Future extensions (draft RFCs):
- multi-step approvals / two-person integrity (RFC-0076)
- repository trust bootstrapping ergonomics (RFC-0078)

## Channels

Channels are namespaced streams with replay/rollback/freeze protections.
Trust policy may also constrain:
- acceptable rollback windows
- required expiry semantics

See RFC-0034 and `docs/61-channel-metadata-tuf-inspired.md`.
Last updated: 2026-02-23
