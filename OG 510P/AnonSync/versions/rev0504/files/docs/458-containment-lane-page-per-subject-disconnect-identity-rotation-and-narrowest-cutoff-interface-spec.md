# Containment lane page: per-subject disconnect, identity rotation, and narrowest-cutoff interface spec

## Purpose

This page answers:

> what is the narrowest believable cutoff I can still perform, and when is that no longer enough?

The page exists because `disconnect`, `unlink`, `rotate`, and `start over` are not the same containment lane.

## Core rule

Every serious seat-compromise case must expose one first-class **Containment lane** page before the operator applies broader rebuild steps.
That page owns:

- available containment lanes
- lane eligibility
- strongest cutoff each lane buys
- strongest residual exposure each lane leaves behind

## Primary layout

The page always renders the same regions:

1. containment verdict
2. lane matrix
3. lane-detail review
4. impossible-or-insufficient actions
5. handoff and receipt

### 1) Containment verdict

Show:

- strongest current recommendation: `subject-local cutoff sufficient`, `mixed lanes needed`, `cohort-wide rotation required`, `insufficient proof`
- narrowest eligible lane
- why narrower lanes fail or survive
- strongest unresolved residual risk

### 2) Lane matrix

Render at least these candidate lanes as rows when relevant:

- `disconnect selected subject`
- `freeze pending offers / approvals / shares`
- `quarantine seat from future arrivals`
- `unlink trusted survivors from current cohort`
- `rotate identity / authority epoch`
- `full rebuild and reissue`

Each row must show:

- scope
- prerequisites
- strongest cutoff it buys
- strongest thing it does **not** cut off
- continuity cost

The operator must be able to answer: **what is the smallest lane that honestly helps?**

### 3) Lane-detail review

For the currently selected lane, show:

- affected seats and subjects
- whether already-landed bytes remain local to the suspect seat
- whether future updates are cut off locally, per subject, or for the whole cohort
- whether downstream reissue, relink, or resharing is still required

The operator must be able to answer: **what does this lane cut off, and what does it leave for later?**

### 4) Impossible-or-insufficient actions

Show a dedicated block for actions that operators often expect but the system cannot honestly promise, such as:

- remote seat unlink unavailable
- already-landed bytes cannot be recalled from the suspect device
- subject disconnect cuts off future updates only
- stale-row hide does not change authority

The operator must be able to answer: **what tempting shortcut is not real here?**

### 5) Handoff and receipt

Link directly to:

- Compromised seat
- Rotation rebuild
- Residual authority

After apply, emit a receipt that preserves:

- chosen lane
- scope touched
- cutoff purchased
- residual exposure still open

## Honest outputs

This page may conclude:

- `disconnect these three advanced subjects now; broader rotation not yet required`
- `subject-local disconnect is insufficient because linked seats remain owners`
- `identity rotation required because remote unlink is unavailable`
- `hide-row action rejected; no containment value`

It may not collapse these into one generic `secure account` flow.

## Rules

### Rule 1 — lane width must be explicit

The page must keep subject-local, seat-local, cohort-wide, and authority-epoch-wide actions visibly separate.

### Rule 2 — every lane needs a non-effect line

Containment is often misunderstood by what it does not do. That non-effect must always render.

### Rule 3 — impossible actions must be shown before destructive escalation

The operator should not discover after broad rotation that the narrower action they wanted never existed.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- which containment lanes are actually available
- which lane is narrowest while still believable
- what cutoff each lane buys
- what already-landed or still-live exposure remains afterward
- when broader identity rotation becomes the honest next step

