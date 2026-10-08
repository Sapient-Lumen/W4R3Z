# Estate certification timeline page: scope change, freshness renewal, and revocation events interface spec

## Purpose

The archive already had campaign timelines.
Once estate certification becomes first-class, it also needs one timeline that shows when scope widened or narrowed, when freshness was renewed or allowed to age, and when the certificate was downgraded or revoked.

## Timeline promise

This page must answer:

> how did this certificate evolve over time, when did its covered scope change, when did evidence age or renew, and what event changed the strongest safe sentence?

## Event families

### 1) Scope-shape events

Supported values:

- `certificate-created`
- `scope-widened`
- `scope-narrowed`
- `exclusion-added`
- `exclusion-removed`
- `separate-certificate-split`

### 2) Witness events

Supported values:

- `required-witness-collected`
- `freshness-renewed`
- `weak-witness-rejected`
- `passive-quiet-window-accepted`
- `freshness-expiry-near`
- `freshness-expired`

### 3) Claim events

Supported values:

- `bounded-certificate-published`
- `family-certificate-published`
- `broader-claim-blocked`
- `broader-claim-unblocked`
- `downgraded-to-weaker-sentence`
- `certificate-retired`

### 4) Revocation events

Supported values:

- `subject-reopened`
- `world-fork-detected`
- `rights-drift-detected`
- `attestation-withdrawn`
- `certificate-revoked`
- `recertification-started`

## Required timeline controls

The page must let operators filter by:

- subject or cohort
- witness family
- claim effect
- exclusion class
- revocation trigger
- time window

## Required summary rail

Pinned above the timeline:

- current strongest safe sentence
- broader blocked sentence
- certified scope count
- excluded scope count
- next freshness expiry
- revocation triggers currently armed

## Explicit anti-goals

Do not:

- show only the initial publication event
- hide scope narrowing after a certificate was published
- collapse freshness expiry and revocation into generic churn
- let exclusion changes vanish once the current sentence looks good

## Why this page exists

Because a certificate is not only a verdict.
It is a living boundary whose truth changes when scope, freshness, or topology changes.
