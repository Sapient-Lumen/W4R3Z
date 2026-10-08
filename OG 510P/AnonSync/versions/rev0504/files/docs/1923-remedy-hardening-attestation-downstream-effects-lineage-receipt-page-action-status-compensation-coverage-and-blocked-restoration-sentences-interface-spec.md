# Remedy-hardening-attestation downstream-effects lineage receipt page — action status, compensation coverage, and blocked restoration sentences

## Purpose

This receipt is the durable summary proving what downstream consequences the stale version caused, what was undone, what was only compensated, what remains irrecoverable, and which stronger restoration sentence the product refused to make.

## Receipt fields

Every downstream-effects lineage receipt must preserve at least:

- case identifier
- source subscriber-invalidation receipt identifier
- current governing receipt identifier
- triggering stale version token
- downstream-effects class at receipt issue time
- named downstream actor coverage
- unknown historical downstream actor flag
- queue-drain posture
- undo coverage class
- compensation coverage class
- irreversibility ceiling class
- highest honest restoration sentence
- strongest blocked restoration sentence
- evidence horizon and known blind spots
- receipt issuer
- receipt issuance time
- next mandatory rereview trigger

## Fixed rendering order

Every downstream-effects lineage receipt must render the same sections in the same order:

1. **Highest honest current restoration sentence**
2. **Triggering stale version and downstream actor coverage**
3. **Undo, compensation, and queue-drain posture**
4. **Irreversibility ceiling and blocked stronger sentence**
5. **Rereview trigger and receipt lineage**

## Hard rules

The receipt must never silently upgrade:

- `downstream actor coverage incomplete` into `restoration complete`
- `compensation complete` into `original state restored`
- `unknown historical actors remain` into `global restoration achieved`
- `current receipt is newer` into `all older effects neutralized`

## Minimum operator questions answered

The receipt must let a later operator answer, without hunting across other pages:

- which stale version is being remediated
- whether downstream consequences are still being discovered, undone, compensated, or merely ceilinged
- which cohort the restoration claim actually covers
- what irreversibility ceiling remains
- which stronger restoration sentence the product intentionally blocked
