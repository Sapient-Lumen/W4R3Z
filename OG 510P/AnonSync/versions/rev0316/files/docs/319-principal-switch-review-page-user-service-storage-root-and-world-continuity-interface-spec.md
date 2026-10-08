# Principal switch review page: user, service, storage root, and world continuity interface spec

## Purpose

This page answers one ordinary question:

> if I change runtime user, service mode, package mode, or storage root, am I still continuing the same local world or creating a successor world that needs reviewed continuity work?

The page exists because `run as service`, `run as current user`, `switch to system`, `change storage path`, and `use config mode` are not harmless toggles.
They can move the seat into a different identity/storage world with different visible inventory and different repair obligations.

## Core decision

Every proposed principal or storage-root change must open one first-class **Principal switch review** page before apply.
That page owns:

- source world identity
- candidate target world identity
- same-world versus successor-world verdict
- expected continuity work
- authority gain or loss
- the next safe step

The workbench must not let `make it work as a service` or `switch user` silently masquerade as a minor preference change.

## Primary layout

The page always renders the same regions in the same order:

1. switch strip
2. source-world card
3. candidate-world card
4. continuity verdict card
5. apply consequences card
6. switch receipts

### 1) Switch strip

Show:

- seat label
- requested change
- current world label
- candidate world label
- current verdict: `same-world`, `successor-world`, `world-ambiguous`, `blocked`
- one next honest action

### 2) Source-world card

This card publishes:

- current execution principal
- current launch mode
- current storage root
- current identity custody summary
- current visible inventory summary

### 3) Candidate-world card

This card publishes:

- candidate execution principal
- candidate launch mode
- candidate storage root
- predicted identity custody source
- predicted visible inventory summary if switched now
- whether the product has strong evidence the candidate world already exists

### 4) Continuity verdict card

This card publishes:

- same-world or successor-world classification
- why that verdict won
- whether re-share / reconnect / rebind work will be required
- whether any current local data becomes hidden, duplicated, or abandoned from the new world's perspective
- minimum safe checkpoint before apply

The operator must be able to answer: **is this a preference change or a reviewed cutover?**

### 5) Apply consequences card

This card publishes:

- authority changes expected after apply
- storage-root changes expected after apply
- inventory visibility changes expected after apply
- safest rollback boundary
- what proof will count as a successful cutover after the switch

### 6) Switch receipts

Receipts show:

- reviewed switch attempts
- accepted or aborted switches
- resulting world identity
- follow-up rebind work
- the actor and time

## Non-negotiable rules

### Rule 1 — empty inventory after switch must be explainable beforehand

If the candidate world is expected to look empty until rebind or re-share, the page must say so before apply.

### Rule 2 — authority gain and world change remain distinct

A switch can increase disk reach while still requiring successor-world continuity work.
The page must not blur those into one `recommended` label.

### Rule 3 — storage-root change is identity-custody change unless proven otherwise

Changing storage root is not cosmetic by default.
Unless continuity is strongly proven, the page must treat it as world-affecting.

## Honest outputs

The page may conclude:

- `Switch to current-user service preserves storage root and remains same-world.`
- `Switch to Local System widens access but creates successor world with separate storage root and empty inventory until reconnect.`
- `Move to explicit config/storage path likely adopts an existing world; confirmation requires identity and share-database match.`
- `Candidate world ambiguous because both roots contain partial state; manual salvage review required before any switch.`

It may not collapse those outcomes into one generic `restart required` notice.
