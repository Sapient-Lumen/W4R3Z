# Remedy-hardening-attestation-freshness lineage receipt page — as-of claim, freshness floor, and blocked stronger sentences

## Purpose

This page is the compact durable receipt for the strongest honest freshness-aware verifier sentence.
It exists so a later verifier can open one page and see whether the sealed bundle is only historically trustworthy or also currently trustworthy as-of a named time and cohort.

## Receipt payload

The receipt must preserve at least:

- case identifier
- source attestation-integrity receipt identifier
- attestation bundle identifier
- seal identifier
- current attestation-freshness posture rung
- historical capture completion time
- explicit as-of claim time
- freshness horizon
- required verifier cohort
- required currentness cohort
- identity fingerprint basis status
- approval carry-forward status
- peer cache status
- history horizon status
- debug-log horizon status
- last revalidation time
- current revocation or challenge status
- highest honest current freshness-aware sentence
- strongest blocked stronger sentence

## Mandatory language rules

The receipt must use scarred language when needed.
Examples:

- `tamper-evident historical proof only`
- `sealed and current for named lanes only`
- `freshness expired; historical integrity remains honest`
- `revalidation pending; stronger live sentence blocked`
- `freshness-aware verifier readiness achieved for required cohort`

## Prohibited overstatements

The receipt must never let these overstatements pass unscarred:

- `sealed` when the operator really means `sealed once, but maybe stale now`
- `current` when the product only knows `not yet contradicted`
- `same identity` when the product only knows `same name or familiar fingerprint`
- `same approval basis` when the product only knows `historically auto-approved`
- `still provable` when the supporting evidence horizon already expired
