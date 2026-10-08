# Remedy-hardening-attestation-integrity contract sheet page — seal, custody, and claim ceiling

## Purpose

This page is the operator's compact contract for whether a case that already achieved an independently verifier-ready hardened baseline may honestly claim that the exported verifier bundle is tamper-evident and custody-preserved.
It exists so the product can distinguish `a verifier could review this bundle` from `later edits, rotations, mutable copies, or clone-like handling cannot silently impersonate the same claim`.

## Core fields

- case identifier
- source remedy-hardening-attestation receipt identifier
- triggering cause family
- current attestation-integrity posture rung
- current hardening class
- attestation bundle identifier
- seal identifier
- seal activation time
- seal algorithm or integrity basis
- custody chain status
- export medium class
- mutable-storage exposure status
- log-rotation exposure status
- config-edit exposure status
- service-world fork exposure status
- unsupported-clone exposure status
- named integrity audience
- required verifier cohort
- highest honest current tamper-evident sentence
- strongest blocked stronger integrity sentence
- next strengthening trigger
- next weakening trigger

## Attestation-integrity posture rungs

The page must model at least these distinct rungs:

- verifier-ready bundle present only
- verifier-ready but unsealed
- seal drafted not yet activated
- sealed for named lanes only
- custody-preserved seal standing
- tamper-evident verifier-ready for required cohort
- integrity challenged
- seal broken or custody collapsed
- integrity claim revoked

## Required distinctions

The page must keep these truths separate:

- verifier-ready versus tamper-evident verifier-ready
- bundle exported versus bundle sealed
- seal present versus seal still standing
- custody recorded versus custody preserved
- storage copy present versus integrity-preserved handoff
- logs captured versus logs protected against later silent replacement
- migrated settings versus invariants re-proven under seal
- named-lane sealing versus required-cohort tamper-evident readiness

## Operator promises

The contract sheet must let the operator say things like:

- `the bundle is verifier-ready, but not yet tamper-evident`
- `seal integrity is honest only for named lanes or named custody hops`
- `copies exist, but mutable-storage exposure still blocks the stronger sentence`
- `the handoff was made, but custody ambiguity remains too high for the stronger claim`
- `the case is now tamper-evident and verifier-ready for the required cohort`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- no seal activated
- seal basis too weak
- custody hop missing
- mutable storage exposure too high
- log rotation or discard risk too high
- config-edit exposure unresolved
- service-world fork ambiguity unresolved
- unsupported clone-like handling not ruled out
