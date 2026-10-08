# Remedy-hardening-attestation subscriber-invalidation timeline page — version issue, revalidate, expiry, and tombstone events

## Purpose

This page is the chronological view of how a case's machine-consumable truth moved through issue, caching, invalidation, expiry, and tombstone stages.
It exists so a later verifier can see not just that the sentence changed, but when subscribers were still allowed to serve the older version, when they were required to revalidate, and when tombstones or freezes became mandatory.

## Event families

The timeline must support at least these event families:

- authoritative version issued
- subscriber first served version
- cache lease started
- must-revalidate boundary reached
- push invalidation sent
- push invalidation confirmed
- pull revalidation completed
- historical snapshot pinned
- public feed frozen
- tombstone published
- successor pointer accepted
- stale serve detected
- stale serve blocked
- subscriber suspended or retired

## Required chronology distinctions

The page must keep these facts visibly separate:

- when the governing receipt changed versus when a subscriber learned of it
- when a lease was still valid versus when it became overdue
- when a stale serve was still authorized versus when it became non-compliant
- when a historical snapshot remained allowed versus when it needed a tombstone pointer
- when a public feed froze versus when it safely resumed

## Timeline views

Every subscriber-invalidation timeline must support at least these views:

### 1) Case-wide chronology

Show all version issues, supersessions, freezes, and tombstone publications in one line.

### 2) Subscriber chronology

For a chosen subscriber or subscriber class show:

- last served version token
- lease start
- must-revalidate time
- invalidation path used
- successor acceptance or tombstone event

### 3) Residual-risk chronology

Show all moments when stale serving remained authorized, became overdue, or was blocked only for part of the subscriber population.

## Required outcome labels

The page must be able to label moments such as:

- `older version still authorized until 14:20 UTC under bounded lease`
- `push invalidation sent, confirmation still pending for external cohort`
- `public feed frozen because successor pointer coverage incomplete`
- `historical audit snapshot retained with non-authoritative watermark only`
- `stale serve detected after lease expiry; blocker remained open until tombstone publication`

## Claim ceilings

The timeline must never imply:

- that version issue time equals subscriber awareness time
- that lease expiry guarantees actual stale bytes vanished
- that tombstone publication on one surface means every subscriber now renders it
- that a resumed feed proves all historical consumers revalidated
