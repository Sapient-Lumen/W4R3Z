# Runtime profile receipt page — executing principal, storage root, surface reach, and follow-up

## Purpose

Produce a durable receipt that records which runtime profile is now active, what continuity verdict the product reached, what storage root and principal are authoritative, which surfaces widened or narrowed, and what follow-up remains.

## Receipt fields

### Identity
- receipt id
- host / seat label
- runtime profile class
- executing principal
- timestamp

### Continuity verdict
- profile lineage verdict
- identity surface verdict
- share carryover verdict
- strongest safe sentence
- stronger blocked sentence if any

### Effective roots and surfaces
- authoritative storage root
- prior profile root if relevant
- WebUI reach posture
- shell / notification / observation posture
- advanced-folder / config-mode posture if relevant

### Requested and effective mutation
- operator requested change
- reviewed effective mutation
- migrate / clean-install / principal-swap / reach-change class
- chosen path (`applied`, `declined`, `deferred`, `compared-only`)

### Follow-up obligations
- reconnect / re-share required?
- retire previous profile row?
- delete old storage root?
- exposure hardening review needed?
- observation caveat to remember?

### Forbidden overclaims
Examples:

- `Nothing important changed.`
- `This is definitely the same seat.`
- `All shares were preserved.`
- `This only changed performance.`
- `The old profile is gone.`

## Entry points

This receipt must be reachable from:

- runtime profile review
- storage lineage forecast
- runtime switch review
- uninstall / replacement flows
- seat-lineage and execution-seat pages

## Success condition

A future reader should be able to tell, without reopening service, storage, config-mode, or uninstall articles, what runtime profile became authoritative, what it inherited, what it did not inherit, what surfaces changed, and what follow-up still remains.
