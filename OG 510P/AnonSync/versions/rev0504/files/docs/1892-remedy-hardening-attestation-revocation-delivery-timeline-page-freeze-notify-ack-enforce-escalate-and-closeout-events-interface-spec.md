# Remedy-hardening-attestation-revocation-delivery timeline page — freeze, notify, acknowledge, enforce, escalate, and closeout events

## Purpose

This page is the chronological spine for revocation delivery and closure.
It exists to preserve the difference between opening a corrective wave, reaching dependents, receiving acknowledgement, suppressing stale surfaces, escalating unreachable dependents, and closing only the portion of the world that was actually proven safe again.

## Event classes

The timeline must support at least these event classes:

- new reliance frozen
- callback path registered
- callback path tested
- corrective notice issued
- delivery confirmed
- acknowledgement requested
- acknowledgement received
- successor receipt bound
- stale surface hidden or retracted
- dependent decision revalidated
- downstream receipt resealed
- unreachable dependent escalated
- reconnect risk re-opened
- named-cohort closure approved
- global closure blocked
- residual-live-surface debt preserved

## Required timeline columns

Every event row must print at least:

- event timestamp
- actor or subsystem
- event class
- affected dependent or surface
- prior closure class
- resulting closure class
- evidence attached
- whether the event upgrades speakability, only preserves history, or reopens risk

## Required chronology guarantees

The timeline must preserve:

- when freeze-new-reliance took effect relative to delivery attempts
- whether acknowledgement was requested before or after a stale surface was hidden
- whether successor binding preceded closure claims
- whether residual-live-surface debt was preserved before or after a named-cohort closure statement
- whether a later reconnect or callback expiry reopened the case

## Required timeline summaries

The page must compute and print:

- first corrective-wave issuance time
- first confirmed delivery time
- first required acknowledgement completion time
- first stale-surface suppression time
- last reopen or escalation time
- named-cohort closure time if any
- current oldest still-open obligation age

## Speakability rules

The timeline must not allow:

- `closed` before the first applicable delivery confirmation
- `acknowledged` before evidence of acknowledgement exists
- `historical only everywhere` before the last required stale surface is suppressed or explicitly preserved as residual risk
- `downstream safe again` without preserving any later reconnect or callback-expiry event that reopens the closure claim
