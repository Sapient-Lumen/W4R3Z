# Action availability page — requested verb, missing basis, and safer-neighbor interface spec

## Purpose

This page answers one ordinary question:

> I want to do a specific thing here — is that exact action available, unavailable for a real semantic reason, temporarily blocked, or simply not present in this seat / edition / posture?

The page exists because a missing control is not self-explanatory.
A hidden button must never silently rewrite intent.

## Core decision

Every serious surface must expose one first-class **Action availability** page whenever:

- the requested action is absent
- the requested action is disabled
- the requested action exists only on some seats / postures / editions
- the visible substitute is stronger than the requested action

The page owns:

- requested verb identity
- current availability verdict
- basis for absence
- nearest safer neighbor
- stronger visible substitutes
- safe sentence afterward

## Primary layout

The page always renders the same regions in the same order:

1. requested action strip
2. availability verdict card
3. absence-basis card
4. neighboring-actions card
5. safest-next-step card
6. receipts

### 1) Requested action strip

Show:

- requested action label
- subject label
- seat / surface label
- current verdict: `available`, `temporarily-blocked`, `posture-impossible`, `capability-missing`, `unknown`
- one honest next action

### 2) Availability verdict card

This card publishes:

- whether the exact action is present in this surface
- whether the exact action exists elsewhere in the product
- whether the action is semantically impossible here or merely unavailable here
- whether a stronger substitute is currently visible

The operator must be able to answer: **is the thing I wanted actually impossible, or just not exposed here?**

### 3) Absence-basis card

This card publishes one row per basis:

- subject posture basis
- seat-class basis
- edition / entitlement basis
- platform or surface basis
- temporary blocker basis
- unknown / diagnostic-needed basis

The page must name the strongest currently proven reason.
`Not available` is not enough.

### 4) Neighboring-actions card

This card lists the nearest lower-risk and higher-risk neighbors:

- gentler action that preserves more bytes / authority / reversibility
- stronger action that removes more, revokes more, or widens blast radius
- whether the requested action sits between them or outside the current ladder

The operator must be able to answer: **what nearby actions exist, and which one is stronger than what I asked for?**

### 5) Safest-next-step card

This card publishes:

- exact next route if the action exists elsewhere
- least-strong substitute if the exact action is missing here
- what proof or capability change would make the requested action available
- what claim ceiling applies if the substitute is used instead

### 6) Receipts

Receipts show:

- requested action
- availability verdict at commit time
- basis for absence or presence
- substitute chosen, if any
- stronger blocked alternatives acknowledged

## Non-negotiable rules

### Rule 1 — missing control must not silently rewrite intent

If the requested control is absent, the product must preserve the original intent and compare substitutes explicitly.

### Rule 2 — capability absence and semantic impossibility must stay separate

`Unavailable in this seat` and `impossible in this subject posture` are not the same truth.

### Rule 3 — stronger visible substitute must be named as stronger

The page must never let the only visible action impersonate the requested one when its consequences are broader.

## Honest outputs

The page may conclude:

- `Disconnect is not available on this seat because this runtime currently exposes only synced-mode removal.`
- `The requested action exists elsewhere in the product, but not in this edition.`
- `Remove is stronger than Disconnect because it widens severance scope from one seat to the linked cohort.`

It may not collapse those outcomes into a generic `button missing` explanation.
