# Intake route review page: join, claim, custody consequence, and safe-switch interface spec

## Purpose

Typed routing alone is not enough.
The operator still needs one last reviewed answer before live commitment:

> if I continue on the currently suggested route, what changes now, what future obligations appear, and when should I deliberately switch to another route instead?

This page exists to make those route consequences explicit.

## Core decision

Every artifact family that can plausibly send the operator down one of several high-stakes routes must expose one first-class **Intake route review** page.

That page owns:

- current route justification
- immediate consequences
- future consequences
- safe route-switch options
- route-review receipt

## Fixed review order

Every intake-route review page must render the same sections in the same order:

1. current route strip
2. immediate consequence card
3. future consequence card
4. safe-switch card
5. blocker and abstention card
6. review receipt promise

### 1) Current route strip

Show:

- current recommended route
- strongest reason this route is recommended
- strongest risk if the recommendation is wrong
- safest next action

Allowed routes:

- `identity join`
- `subject claim`
- `encrypted custody setup`
- `stop without commitment`

The operator must be able to answer: **what route is currently on deck, and why?**

### 2) Immediate consequence card

Show what would change *right now* if the operator continues:

- new seat/family relationship
- new subject bind
- new ciphertext custody node
- local target review requirement
- current receipt that would be emitted

The operator must be able to answer: **what concrete thing gets created or changed immediately?**

### 3) Future consequence card

Show what later obligations or side effects come with the route:

- identity-join future-subject fanout and takeover implications
- subject-claim approval, permission, or ongoing sync implications
- encrypted-custody recovery burden and capability ceilings
- later review pages that become ordinary maintenance surfaces

The operator must be able to answer: **what ongoing burden do I accept if I take this route?**

### 4) Safe-switch card

This section is mandatory whenever another plausible route exists.

For each alternative route, show:

- semantic difference from the current route
- what risk is avoided
- what value is lost
- which deeper page would open instead

Example rows:

- `Switch from identity join to subject claim` — avoid whole-family adoption; lose automatic future-subject availability
- `Switch from subject claim to encrypted custody` — avoid plaintext bind on destination; accept ciphertext-only ceiling and recovery burden
- `Stop and clear intake` — avoid uncertain commitment; lose immediate progress

The operator must be able to answer: **when should I deliberately choose a different route?**

### 5) Blocker and abstention card

Show:

- exact blockers still unresolved
- whether uncertainty is about parse, target, posture, or continuity
- whether abstaining is safer than proceeding
- strongest next non-destructive action

The product must make `do nothing yet` an intelligible success state when review confidence is too low.

### 6) Review receipt promise

A route-review receipt must preserve:

- recommended route
- justification
- alternatives shown
- operator choice
- blocker state at decision time
- onward page or stop result

The operator must be able to answer later: **which route was recommended, what alternatives were on the table, and what did I choose?**

## Acceptance criteria

This spec is satisfied when:

- current route and alternative routes are compared explicitly
- immediate consequences and future obligations are both visible before commitment
- route switch preserves semantic honesty rather than feeling like a cosmetic navigation change
- abstention is available and leaves a useful receipt
