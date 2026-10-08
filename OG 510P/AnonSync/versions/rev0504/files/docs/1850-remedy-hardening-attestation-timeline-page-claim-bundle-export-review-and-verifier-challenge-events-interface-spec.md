# Remedy-hardening-attestation timeline page — claim, bundle export, review, and verifier challenge events

## Purpose

This page is the ordered event surface for how a case moved from bootstrap-reproducible safety into evidence bundling, verifier review, successor handoff, challenge, or later attestation decay.
It exists so later readers can see attestation timing directly rather than reconstructing it from log collection and support workflows.

## Event types

The timeline must support at least these event kinds:

- bootstrap receipt imported
- attestation review opened
- bundle identifier assigned
- storage snapshot captured
- config snapshot captured
- history horizon recorded
- debug logging enabled
- debug logging restart required
- issue reproduction recorded
- evidence wait window completed
- log provenance accepted
- log provenance challenged
- folder-type coverage limited
- lane coverage expanded
- successor handoff bundle exported
- independent verifier review completed
- attestation ceiling raised
- attestation expiry clock started
- attestation staleness warning issued
- attestation challenge opened
- attestation collapsed or revoked
- re-attestation completed

## Timeline queries

The page must answer:

- when did bootstrap reproducibility stop being the strongest honest sentence?
- when was the first verifier-ready bundle generated?
- when did provenance or horizon weakness first block the stronger sentence?
- when did successor-handoff readiness become honest?
- when did later staleness or challenge collapse the attestation claim?

## View modes

The page must provide:

- all-events view
- bundle-generation view
- provenance view
- coverage view
- challenge-only view
- expiry-only view
- re-attestation-only view
