# Remedy-hold-enforcement review page — is this preservation hold actually binding where it needs to be?

## Decision question

This page answers one operational question:

**Is the preservation hold actually binding across the custodians and cleanup paths that matter, or are we still relying on ordinary ops behavior and hope?**

## Review sections

### 1) Hold scope versus enforcement scope

The review must begin by comparing the declared hold scope with the enforcement scope actually achieved.
It must show:

- which protected material classes are in scope
- which custodians truly hold those materials
- which custodians have acknowledged the hold
- which cleanup or deletion paths are still unsuppressed

### 2) Custodian acknowledgment map

The page must separate:

- declared custodians
- responsive custodians
- acknowledged custodians
- delegated or indirect custodians
- custodians whose current authority to bind preservation is stale or disputed

### 3) Cleanup-path suppression map

The review must show whether the hold is resilient against the practical ways substrate disappears, including:

- Archive aging or purge
- Archive disablement
- manual clear or local deletion
- placeholder dehydration or reclaim behavior
- revocation or folder removal policies
- low-space cleanup pressure
- restart-sensitive settings not yet applied

### 4) Detection and blind-spot analysis

The review must model whether a breach would even be noticed in time.
It must separate:

- immediate breach visibility
- warning-only visibility
- visibility delayed to periodic rescan
- visibility absent on some environments
- environments whose warnings may be ignored as ordinary operational noise

### 5) Highest honest sentence

The page must always conclude with one highest honest sentence from this family:

- `hold declared only`
- `hold acknowledged partial`
- `hold enforced partial`
- `hold enforced for required custodians but with blind spots`
- `hold enforced and breach-sensed for required cohorts`
- `hold breached`
- `enforcement collapsed`

It must also name the blocked stronger sentence and why it remains blocked.

## Review invariants

- the review never lets acknowledgment impersonate enforcement
- the review never lets enforcement impersonate breach detectability
- the review never lets `no breach observed` impersonate `no breach plausible within coverage`
- the review always names the exact custodian, path, or blind spot that blocks the stronger sentence
