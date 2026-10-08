# Future-arrival defaults page — scope, default root, and manual-bind right interface spec

## Purpose

Give the operator one exact answer to:

- what later arrivals on this seat will do by default
- what root or template will be suggested for them
- what the current seat default does **not** decide
- whether one-share bind choice remains available without changing whole-seat posture

This page is the standing-default companion to `164-future-arrival-defaults-placement-memory-and-device-wide-posture-boundary-interface-spec.md`, the mode-split companion to `617-current-sync-mode-page-current-share-future-default-and-path-basis-interface-spec.md`, and the placement-suggestion companion to `99-arrival-placement-suggestion-and-collision-review-interface-spec.md`.

## Inputs

- seat identifier
- reviewed scope (`all linked-device arrivals`, `family arrivals`, `member-class arrivals`, `workspace arrivals`, `unknown`)
- visibility default
- materialization default
- default root / template status
- default root provenance (`operator-reviewed`, `imported`, `remembered`, `policy-derived`, `unknown`)
- manual-bind right (`always-available`, `available-with-compare`, `temporarily-blocked`, `unknown`)
- current-share impact sentence
- strongest safe sentence
- stronger forbidden sentence
- nearest honest next action

## Primary questions this page must answer

1. What exactly do later arrivals on this seat do by default?
2. Which root or template will be suggested?
3. Does this default affect the current already-present share?
4. May I still place one arriving share manually without mutating the whole seat posture?
5. What sentence is the product still allowed to say about duplicate avoidance and bind safety?

## Layout

### A. Default verdict strip

Fields:

- seat label
- reviewed scope
- visibility default
- materialization default
- default root summary
- strongest safe sentence

Example verdicts:

- `Future arrivals on Home-NAS announce immediately, suggest placeholder-backed start, and propose /srv/incoming; one-share manual bind remains available.`
- `Family arrivals suggest /Users/alex/AnonSync and full local bytes, but existing shares are unchanged and a single arriving share can still override the suggestion.`

### B. Scope card

Show:

- reviewed scope
- why this scope was chosen
- whether the default is seat-wide, family-wide, or narrower
- who may edit it

This card exists so the operator does not confuse a family default with one-share truth.

### C. Default-effects card

Show separately:

- default visibility effect
- default materialization suggestion
- default root/template suggestion
- whether these are suggestion, automatic draft creation, or stronger automation

The operator must be able to answer: `what will happen later if I do nothing?`

### D. Manual-bind-right card

Show:

- whether a one-share manual bind remains available
- whether compare review is required before the bind can complete
- whether using the manual bind right changes the seat default or leaves it untouched
- strongest safe sentence about one-share override

Example:

- `You may place this arriving share manually. The seat default remains /srv/incoming for later arrivals unless you change it separately.`

### E. Current-share-independence card

Show:

- explicit sentence about whether editing this page changes any existing share
- whether the current share detail page is merely reflecting this default or actually independent now
- next honest route to edit one current share without changing defaults

### F. Duplicate-policy card

Show:

- whether same-name collisions trigger review, compare, adopt, or outright block
- whether suffix fallback is allowed (`never` by default for managed binds)
- what evidence would be needed for safe adoption of an existing directory

### G. Claim-ceiling card

Show together:

- strongest approved sentence
- stronger forbidden sentence
- blocker basis

Example:

- approved: `Future arrivals here will be suggested into /srv/incoming, but one-share bind choice stays reviewable.`
- forbidden: `All shares arriving here will safely bind to /srv/incoming automatically.`
- blocker basis: `non-empty-target and same-name collisions still require share-specific review`

## Compact row contract

A truthful compact default row should preserve this order:

1. seat + scope
2. visibility default
3. materialization default
4. default root
5. manual-bind right
6. next honest action

Example:

```text
Home-NAS / family arrivals    announce now    placeholder start    root: /srv/incoming    manual bind: yes    Review
```

## Success criteria

A good page lets a later operator answer:

1. what later arrivals will do by default
2. what root will be suggested
3. whether the current share changes at all
4. whether one-share placement remains available without whole-seat mutation
5. whether duplicate handling is suggestion, review, adopt, or block
