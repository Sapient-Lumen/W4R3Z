# Remedy-hardening-attestation-integrity lineage receipt page — seal, custody, verifier readiness, and blocked stronger sentences

## Purpose

This receipt is the portable summary of the strongest honest claim about a case that already achieved independent verifier readiness and now attempts to claim tamper-evident integrity.
It exists so later operators can answer `is this merely verifier-ready, or is it also sealed and custody-preserved strongly enough that later mutation cannot silently impersonate the same claim?` from one durable object.

## Receipt fields

- receipt identifier
- case identifier
- source remedy-hardening-attestation receipt identifier
- triggering cause family
- current attestation-integrity posture rung
- current hardening class
- attestation bundle identifier
- seal identifier
- seal activation time
- seal basis summary
- custody-chain summary
- export-medium summary
- mutable-storage exposure summary
- log-rotation exposure summary
- config-edit exposure summary
- service-world fork exposure summary
- unsupported-clone exposure summary
- named integrity audience
- required verifier cohort
- highest honest current tamper-evident sentence
- strongest blocked stronger integrity sentence
- next mandatory strengthening trigger
- next automatic weakening trigger

## Mandatory sentence discipline

The receipt must preserve these distinctions:

- verifier-ready versus tamper-evident verifier-ready
- bundle exported versus bundle sealed
- seal activated versus seal still standing
- custody recorded versus custody preserved
- storage copy versus integrity-preserved handoff
- logs captured versus sealed provenance
- migrated settings versus invariants re-proven under seal
- named-lane integrity versus required-cohort integrity
- independently verifier-ready discharge versus tamper-evident independently verifier-ready discharge

## Example summary sentences

- `The hardened baseline is independently verifier-ready, but not yet tamper-evident.`
- `Seal integrity is honest only for named lanes or named custody hops; stronger language stays blocked by mutable-surface exposure.`
- `A later verifier can inspect the bundle, but seal-preserved integrity remains blocked.`
- `The attestation bundle is now tamper-evident and verifier-ready for the required cohort.`
- `Integrity status later decayed, was challenged, or collapsed.`
