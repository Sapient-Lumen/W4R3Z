# Remedy-hardening-retention contract sheet page — drift, scope retention, and carry-forward audit

## Purpose

This page is the operator's compact contract for whether a case that already claimed recurrence hardening has actually retained that hardening across later drift, overrides, onboarding, and scope expansion.
It exists so the product can distinguish `we deployed a durable control once` from `that control is still retained for the required cohort and future carry-forward surface now`.

## Core fields

- case identifier
- source remedy-hardening receipt identifier
- triggering cause family
- current hardening-retention posture rung
- original hardening strategy class
- current retained-versus-drifted control class
- required retention cohort
- current retained scope achieved
- future carry-forward surface class
- linked-identity spread retention status
- manual-override divergence status
- peer-local rule divergence status
- service or storage-world continuity status
- lower-permission retention status
- sync-mode retention status, if relevant
- strongest honest current retained-hardening sentence
- strongest blocked stronger recurrence-retained sentence
- next strengthening trigger
- next weakening trigger

## Remedy-hardening-retention posture rungs

The page must model at least these distinct rungs:

- recurrence hardening achieved once; retention unreviewed
- hardening retained for named lane only
- drift suspected; stronger retained-hardening sentence blocked
- manual override detached one lane from current defaults
- peer-local rule divergence detected
- service or storage-world fork reopened review
- required-cohort retention pending carry-forward closure
- required-cohort hardening retained
- future carry-forward retention pending
- recurrence-hardened-and-retained discharge achieved
- hardening-retention collapsed or rolled back

## Required distinctions

The page must keep these truths separate:

- hardening achieved once versus hardening still retained now
- required original cohort retained versus future carry-forward surface retained
- default policy present versus every manually altered lane still aligned
- same-looking preference state versus same effective behavior across all peers
- linked identity healthy versus later-linked spread still retention-safe
- same service uptime versus same storage world and same policy world
- narrowed recurrence risk versus retained recurrence hardening

## Operator promises

The contract sheet must let the operator say things like:

- `the case was hardened once, but one manually altered share no longer follows the current default, so the stronger retained-hardening sentence stays blocked`
- `IgnoreList divergence across peers reopened risk interpretation, so required-cohort retention remains unproven`
- `the original cohort retained the guardrail, but linked-device carry-forward for later folders is still outside the retained-hardening scope`
- `a service-principal and storage-world switch reopened review because the original hardened state did not automatically carry into the new world`
- `retention now survives overrides, carry-forward, and scope expansion, so recurrence-hardened-and-retained discharge is honest`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- retention unreviewed
- drift suspected
- manual override detached lane
- peer-local rule divergence
- linked-device carry-forward reopened
- lower-permission or admission downgrade not retained
- service or storage-world discontinuity
- evidence basis too weak to claim retained hardening
