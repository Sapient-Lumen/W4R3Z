# Remedy-hardening-attestation-freshness timeline page — seal, expiry, revalidation, and revocation events

## Purpose

This page is the chronological surface for everything that can strengthen or weaken freshness-aware verifier trust after sealing.
It exists so later readers can see how a case moved from historical proof toward live currentness, and when it fell back again.

## Timeline events

The page must preserve at least these event classes:

- seal activated
- historical capture completed
- as-of claim issued
- freshness horizon set
- freshness-horizon warning issued
- freshness expired
- identity recreated or unlinked
- linked-device approval carry-forward changed
- peer cache cleared or re-expired
- history horizon fell below threshold
- log rotation or discard crossed proof floor
- revalidation requested
- revalidation passed
- revalidation failed
- revocation challenge opened
- revocation challenge cleared
- freshness-aware verifier readiness collapsed

## Event rules

The timeline must show:

- exact event time
- event class
- affected cohort or lane
- whether the event strengthened or weakened the current claim ceiling
- the strongest sentence made newly honest or newly blocked by that event
- whether the event was reversible, sticky, or scar-bearing

## Reader outcome

A reader opening only this timeline must be able to tell:

- when the bundle was merely sealed historically
- when it became current enough for named or required cohorts
- when freshness warnings or expiry began
- whether identity or approval changes forced revalidation
- whether revocation or challenge ever reopened the case
- why the present strongest sentence is still honest now
