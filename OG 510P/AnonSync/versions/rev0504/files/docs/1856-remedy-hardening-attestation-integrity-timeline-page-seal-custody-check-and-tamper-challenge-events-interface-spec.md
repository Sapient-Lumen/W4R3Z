# Remedy-hardening-attestation-integrity timeline page — seal, custody check, and tamper challenge events

## Purpose

This page is the ordered event surface for how a case moved from independently verifier-ready evidence into sealing, custody-preserved export, tamper challenge, or later integrity collapse.
It exists so later readers can see integrity timing directly rather than reconstructing it from storage copies, service changes, and support workflows.

## Event types

The timeline must support at least these event kinds:

- verifier-ready receipt imported
- integrity review opened
- seal identifier assigned
- seal activated
- custody hop recorded
- custody hop challenged
- mutable-storage exposure recorded
- log rotation exposure recorded
- config-edit exposure recorded
- service-world fork recorded
- clone-like handling warning recorded
- integrity ceiling raised
- named-lane-only seal warning issued
- seal challenge opened
- seal break confirmed
- custody collapsed
- integrity claim revoked
- re-seal completed
- re-attestation completed

## Timeline queries

The page must answer:

- when did independent verifier readiness stop being the strongest honest sentence?
- when was the first honest seal activated?
- when did mutable-surface exposure first block the stronger sentence?
- when did custody become strong enough for the required cohort?
- when did later tamper challenge or seal break collapse the integrity claim?

## View modes

The page must provide:

- all-events view
- seal-only view
- custody-only view
- mutable-surface view
- challenge-only view
- collapse-only view
- re-seal-only view
