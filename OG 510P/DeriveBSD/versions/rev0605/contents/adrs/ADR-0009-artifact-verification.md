# ADR-0009: Artifact verification is mandatory (digests + signatures + optional attestations)

- Status: **accepted**
- Date: 2026-02-23

## Context

DeriveBSD assumes:
- mirrors/caches are hostile blob stores
- builders may be compromised
- rollback/freeze/mix-and-match attacks are realistic at the distribution layer

## Decision

1) **Every artifact is identified by an immutable digest** (store path / bundle digest).
2) **No artifact is *accepted* unless verified**:
   - digest match (content integrity)
   - signature verification against a policy-selected key (authenticity)
3) **Policy may additionally require attestations** (e.g., provenance) bound to the artifact digest.
4) **Update metadata must be replay-safe**:
   - channel metadata uses explicit versioning/expiration rules (TUF-inspired)
   - rollbacks require an explicit override that is logged and policy-governed

## Consequences

- Mirrors are untrusted: “trust” lives in signatures, attestations, and policy.
- Offline/online key separation becomes important (see `docs/47-key-management.md`).
- Clients persist “latest seen” channel state to detect rollback/freeze attempts.
- Operational escape hatches exist, but are always explicit and auditable.

## References (authoritative)

- TUF specification (rollback/freeze protections, consistent snapshots): https://theupdateframework.github.io/specification/latest/
- SLSA spec FAQ (SLSA ↔ in-toto attestations): https://slsa.dev/spec/v1.1/faq
- in-toto Attestation Framework specs (Statement + DSSE envelope): https://in-toto.io/docs/specs/

