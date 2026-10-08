# Allocation occupancy lineage receipt page — winning room, activation state, and blocked stronger sentences

## Purpose

This receipt is the stable handoff object for the truth about awarded room after contention verdict.
It preserves not just who won, but whether the room was actually activated, whether it drifted idle, and whether reclaim or reopened contention followed.

## Required fields

### Identity

- contention case id
- winning claimant id
- awarded room amount
- award class
- receipt issue time

### Current strongest true sentence

One of:

- `awarded-not-activated`
- `activated-and-productive`
- `activated-but-no-net-progress`
- `idle-held`
- `downgraded-pending-activation`
- `reclaimed`
- `reopened-for-new-verdict`

### Basis block

- activation deadline
- last motion time
- last net-advance time
- blocker class if any
- loser starvation age
- reserve exception yes/no

### Consequence block

- loser sentence still blocked
- reclaim trigger if still outstanding
- next review or expiry time
- who regains eligibility if reclaim occurs
- stronger sentence unavailable and why

## Receipt obligations

- keep award truth and occupancy truth separate
- preserve idle-held state as a public truth rather than a private operator note
- show reclaim or reopen as typed outcomes
- preserve the sentence ceiling for both winner and losers
- remain readable without the full timeline open

## Stronger-sentence guard

The receipt may say `this claimant won the room`.
It may not say `this claimant still deserves the room` unless the current basis supports continued protected occupancy.