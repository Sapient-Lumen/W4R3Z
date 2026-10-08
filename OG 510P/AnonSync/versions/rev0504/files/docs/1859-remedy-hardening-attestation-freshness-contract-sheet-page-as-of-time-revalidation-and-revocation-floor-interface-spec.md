# Remedy-hardening-attestation-freshness contract sheet page — as-of time, revalidation, and revocation floor

## Purpose

This page is the operator's compact contract for whether a case that already achieved tamper-evident independently verifier-ready standing may honestly claim that the bundle is still current enough to trust now.
It exists so the product can distinguish `sealed historical proof exists` from `sealed proof is still fresh, revalidated, and safe to use as a live verifier sentence`.

## Core fields

- case identifier
- source attestation-integrity receipt identifier
- triggering cause family
- current attestation-freshness posture rung
- attestation bundle identifier
- seal identifier
- seal standing status
- historical capture completion time
- as-of claim time
- freshness horizon
- freshness budget remaining
- required verifier cohort
- required currentness cohort
- identity fingerprint basis status
- linked-device approval carry-forward status
- peer cache or routing cache status
- history horizon coverage status
- debug-log horizon coverage status
- revalidation required flag
- last revalidation time
- last revalidation actor or lane
- revocation or identity challenge status
- highest honest current freshness-aware sentence
- strongest blocked stronger freshness-aware sentence
- next strengthening trigger
- next weakening trigger

## Attestation-freshness posture rungs

The page must model at least these distinct rungs:

- sealed historical bundle only
- sealed and current for named lanes only
- freshness horizon near expiry
- freshness expired but historical integrity still stands
- revalidation requested
- revalidation passed for named cohort only
- freshness-bounded verifier-ready for required cohort
- revocation challenge open
- freshness-aware verifier readiness collapsed

## Required distinctions

The page must keep these truths separate:

- tamper-evident versus currently trustworthy
- sealed historical proof versus sealed live proof
- as-of time versus seal activation time
- freshness horizon versus integrity standing
- history coverage versus currentness coverage
- log capture horizon versus present-world revalidation
- remembered approval versus currently re-accepted approval basis
- fingerprint continuity versus identity continuity fully re-proven
- cache cleared once versus cache-sensitive truth revalidated now

## Operator promises

The contract sheet must let the operator say things like:

- `the bundle remains sealed, but only as a historical proof`
- `freshness has degraded and the stronger live-verifier sentence is blocked`
- `identity continuity still looks plausible, but revalidation is required before the stronger sentence`
- `history and logs remain honest as of capture time, yet currentness is no longer honest`
- `the case is now sealed, fresh, and revalidated for the required verifier cohort`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- freshness horizon expired
- revalidation overdue
- identity continuity unresolved
- approval carry-forward no longer acceptable
- peer cache or routing cache ambiguity unresolved
- history horizon too short
- log horizon too short or rotated away
- revocation or challenge unresolved
