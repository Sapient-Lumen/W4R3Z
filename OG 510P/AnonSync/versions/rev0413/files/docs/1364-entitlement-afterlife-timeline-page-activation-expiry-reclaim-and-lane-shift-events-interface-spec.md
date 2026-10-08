# Entitlement-afterlife timeline page — activation, expiry, reclaim, and lane-shift events

## Purpose

This page keeps entitlement truth chronological.
It exists so the product can explain how a capability moved between trial, active, revocable, expired, unsupported, or reactivated states over time.

## Required event classes

### 1) Activation-issued / activation-renewed

Examples:

- site-issued v3 non-commercial license applied
- legacy Home Pro or Family Pro key applied
- Business owner key applied
- owner re-applied updated key

### 2) Ownership / seat shift

Examples:

- Business key applied on another identity and ownership moved
- seat shared to another participant
- seat reclaimed
- linked device joined or left owner identity

### 3) Expiry / trial horizon shift

Examples:

- 7-day v3 post-upgrade trial began
- 14-day Business trial expired
- subscription expired
- license renewed

### 4) Support-lane shift

Examples:

- moved from workstation to server posture
- server-support qualifier gained
- updated toward v3 and lost Business eligibility
- remained on v2 because business lane required it

### 5) Feature cliff / restoration

Examples:

- local shares ceased syncing on entitlement loss
- Pro feature set returned after re-apply
- business sharing/linking stopped on wrong server-support posture
- seat regained after owner re-shared

## Timeline output rules

- Every event must say whether it changed **source**, **topology**, **legitimacy**, **feature-afterlife**, or **support posture**.
- Every event must say whether the stronger sentence `legitimately entitled now` widened, narrowed, or remained blocked.
- Every ownership or seat event must say whether current access became more independent or more revocable.

## Final timeline sentence

The page must end with one summary sentence in this shape:

> `Current entitlement class is the result of <latest governing event>; stronger sentence <...> remains blocked because <...>.`
