# Remedy-hardening-attestation-corroboration contract sheet page — independent planes and claim floor

## Purpose

This page is the operator's compact contract for whether a case that already achieved tamper-evident and freshness-bounded independently verifier-ready standing may honestly claim that the strongest sentence is corroborated across sufficiently independent evidence planes.
It exists so the product can distinguish `the bundle still looks good somewhere` from `the bundle's strongest sentence is independently corroborated across the required planes`.

## Core fields

- case identifier
- source attestation-freshness receipt identifier
- triggering cause family
- current attestation-corroboration posture rung
- attestation bundle identifier
- required evidence-plane set
- required independence floor
- required verifier cohort
- required world set
- desktop UI plane status
- WebUI plane status
- storage-folder plane status
- runtime or service plane status
- debug-log plane status
- config or startup-authority plane status
- last cross-plane comparison time
- cross-plane contradiction status
- stale-plane mask
- same-source reuse mask
- dominant-plane warning status
- highest honest corroborated sentence
- strongest blocked stronger corroborated sentence
- next strengthening trigger
- next weakening trigger

## Attestation-corroboration posture rungs

The page must model at least these distinct rungs:

- single-plane evidence only
- two-plane corroborated for named lanes only
- required plane missing
- corroboration pending across required planes
- same-world corroboration only
- independent-plane floor not met
- contradiction open across planes
- corroborated for required verifier cohort
- corroboration collapsed

## Required distinctions

The page must keep these truths separate:

- multiple observations versus independent corroboration
- same rendering twice versus separate planes
- same storage world versus separate world corroboration
- quiet UI versus corroborated runtime
- log evidence present versus log evidence independent enough to strengthen the claim
- config snapshot present versus live plane agreement
- missing plane versus contradictory plane
- stale plane versus fresh plane

## Operator promises

The contract sheet must let the operator say things like:

- `the bundle is still fresh, but only single-plane credible`
- `the storage and log planes agree, yet the stronger sentence is blocked until presentation or runtime corroboration also passes`
- `the UI looked healthy, but that is only a dominant-plane clue, not the corroborated verdict`
- `cross-plane contradiction opened, so the stronger sentence degraded even though one plane still looks calm`
- `the case is now sealed, fresh, and independently corroborated across the required planes`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- required plane missing
- independence floor not met
- dominant plane overload
- stale plane beyond freshness budget
- cross-world mismatch unresolved
- contradiction open
- evidence derived only after restart or forced capture
- support-only workflow not yet corroborated by durable plane
