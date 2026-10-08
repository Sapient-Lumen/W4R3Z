# Allocation envelope lineage receipt page — awarded room, conformance class, and blocked stronger sentences

## Purpose

This receipt is the stable handoff object for the truth about whether an active winner stayed inside the room it was actually awarded.
It preserves not just that the winner was active, but whether that use remained in bounds, drifted outward, touched protected reserve, and was corrected or reclaimed.

## Required fields

### Identity

- contention case id
- winning claimant id
- awarded room amount
- receipt issue time
- current award class

### Current strongest true sentence

One of:

- `active-within-envelope`
- `active-at-envelope-edge`
- `active-with-valid-temporary-borrow`
- `active-overdrawn`
- `active-breaching-protected-reserve`
- `corrected-back-into-conformance`
- `reclaimed-after-envelope-breach`
- `reopened-after-envelope-failure`

### Basis block

- latest measured consumption
- measurement confidence
- reserve exception yes/no
- reserve impact yes/no
- impacted claimant set
- next review or expiry time

### Consequence block

- strongest blocked winner sentence
- strongest blocked loser/neighbor sentence
- correction or reclaim trigger if still open
- reserve restoration state
- stronger sentence unavailable and why

## Receipt obligations

- keep award truth, occupancy truth, and envelope truth separate
- preserve reserve breach as public truth rather than private operator commentary
- show correction, reclaim, or reopen as typed outcomes
- preserve the sentence ceiling for both winner and impacted claimants
- remain readable without the full timeline open

## Stronger-sentence guard

The receipt may say `this claimant is active`.
It may not say `this claimant is staying inside the awarded room` unless the current basis supports that stronger sentence.
