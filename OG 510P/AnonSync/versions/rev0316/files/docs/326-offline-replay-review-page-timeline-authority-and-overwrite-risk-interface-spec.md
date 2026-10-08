# Offline replay review page: timeline authority and overwrite risk interface spec

## Purpose

This page answers one ordinary question:

> when a peer edited while offline and is now returning, what timeline is competing, which version is currently favored, what gets overwritten, and what preservation proof exists before apply?

The page exists because `latest change`, `newer file`, and `latest peer to come online` are not the same authority rule.

## Core decision

Any time an offline-returning edit can displace already-propagated online edits, the product must open one first-class **Offline replay review** page.
That page owns:

- competing timeline candidates
- current authority rule in force
- overwrite risk
- preservation promise for losing material
- safer alternatives when the winner is surprising

The operator must not have to learn this from a conflict FAQ after the overwrite already happened.

## Primary layout

The page always renders the same regions in the same order:

1. incident strip
2. competing timeline card
3. authority-ranking card
4. overwrite and preservation card
5. action matrix
6. replay receipts

### 1) Incident strip

Show:

- subject path or subject cluster
- offline-returning seat
- currently threatened seat or seats
- verdict: `online-order-clean`, `offline-return-dominant`, `authority-ambiguous`, `blocked-for-review`
- one next honest action

### 2) Competing timeline card

This card publishes:

- all candidate versions in play
- where each was authored
- whether authored online or offline
- authored time and return time, each clearly separated
- whether the candidate is already present on other peers

The operator must be able to answer: **what actually happened on which timeline?**

### 3) Authority-ranking card

This card publishes:

- current ranking rule in force
- why the tentative winner is winning: `clean chronological winner`, `offline-return winner`, `manual settlement`, `unknown`
- chronology confidence for each candidate
- whether the ranking is surprising relative to ordinary time order

The operator must be able to answer: **why is this version winning, and is the rule itself unusual here?**

### 4) Overwrite and preservation card

This card publishes:

- which versions will be overwritten if nothing changes
- where losing bytes will be preserved
- retention horizon and access path for preserved losers
- whether the threatened seat still holds the easiest full-copy recovery path

The operator must be able to answer: **what exactly would be lost from the live path, and how well is it preserved?**

### 5) Action matrix

This card publishes:

- allow returning offline version to replay
- hold and require manual settlement
- preserve both versions and quarantine the loser from live replay
- export or branch the returning version instead of letting it overwrite live state

Each action shows its replication scope and receipt promise.

The operator must be able to answer: **what are the safe alternatives to a surprising overwrite?**

### 6) Replay receipts

Receipts show:

- candidates reviewed
- authority rule applied
- losing-version preservation location
- final winner and scope

## Non-negotiable rules

### Rule 1 — authored time and return time must stay distinct

The product must never let `edited at` and `came back online at` silently blur together.

### Rule 2 — surprising offline dominance must be named

If a chronologically earlier offline edit can outrank a later online edit, the page must say so directly.

### Rule 3 — loser preservation must be explicit before apply

Archive, branch, quarantine, or none must be shown before the overwrite is allowed.

## Honest outputs

The page may conclude:

- `This returning offline version will overwrite a later online edit because current replay authority favors the latest file to come online.`
- `Chronological order and replay authority diverge here; manual settlement is safer than silent propagation.`
- `Allowing replay is acceptable because the losing online edit is preserved and the threatened seat no longer holds the only easy recovery copy.`

It may not collapse those outcomes into one generic `conflict resolved` badge.
