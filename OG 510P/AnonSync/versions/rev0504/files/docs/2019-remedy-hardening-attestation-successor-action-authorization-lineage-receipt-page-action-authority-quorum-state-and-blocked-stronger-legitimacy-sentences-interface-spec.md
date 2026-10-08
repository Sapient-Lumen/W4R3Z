# Remedy-hardening-attestation successor action authorization lineage receipt page — action authority, quorum state, and blocked stronger legitimacy sentences

## Purpose

This page is the compact receipt a product can carry forward after reviewing whether a named successor-world action was legitimately authorized.
It exists so downstream users can quote one durable object instead of reconstructing action legitimacy from owner defaults, remembered approvals, and link-security checkboxes.

## Receipt body

Every successor-action-authorization receipt must contain:

- receipt identifier
- successor-action-authorization case identifier
- source successor-controller-roster receipt identifier
- successor world identifier
- governed slice identifier
- named action identifier
- action family and risk class
- requested actor set
- satisfied actor set if any
- current quorum state
- current step-up state
- remembered-authorization reuse state
- authorization scope class
- execution window or expiry horizon
- highest honest public sentence
- strongest blocked stronger sentence
- specific contradiction set that blocks the stronger sentence
- next evidence needed for upgrade
- downgrade trigger set
- receipt issue time
- receipt expiry or mandatory re-review horizon

## Allowed highest honest public sentences

The receipt may expose sentences such as:

- controller roster known, action gate not yet reviewed
- routine action allowed for named actor only
- high-risk action blocked pending second controller
- fresh step-up proof missing, action blocked
- emergency containment allowed, broader mutation blocked
- named action authorized once for named slice only
- reusable standing authorization still blocked
- broader family authorization blocked

## Forbidden upgrades

The receipt must never allow:

- `authorized action` without naming the action family or slice
- `quorum satisfied` when a second controller was only historically approved but not presently participating
- `fresh approval` when remembered authorization actually did the work
- `standing privilege established` from one one-shot authorization
- `high-risk action legitimate` when the action actually rode on unchecked auto-connect or lower-burden convenience settings

## Receipt downgrade triggers

The receipt must automatically become stale or downgraded when:

- the authorization window expires before execution
- a contradiction shows the actor set was broader or weaker than stated
- remembered approval was used where fresh approval was required
- a later rulebook revision raises the burden for this action class
- the action family broadens beyond the named slice or named one-shot execution
- new evidence shows an emergency exception was used outside its permitted class
