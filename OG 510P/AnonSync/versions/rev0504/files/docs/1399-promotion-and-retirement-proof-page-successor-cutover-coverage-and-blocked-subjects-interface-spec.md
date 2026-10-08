# Promotion and retirement proof page — successor cutover, coverage, and blocked subjects

## Purpose

This page is the last pre-commit proof before the product publishes a new current policy or retires an old one.
It answers:

> are we actually ready to promote this successor and/or retire this predecessor, for what exact coverage, with what exceptions, and with what rollback class?

## Core decision

Every serious lifecycle mutation must emit one **Promotion and retirement proof** page before commit.
The proof is stricter than review.
It compiles the final action contract.

## Fixed page order

1. action proof strip
2. promotion proof card
3. retirement proof card
4. subject-outcome card
5. waiver-resolution card
6. activation-and-rollback card
7. commit receipt

### 1) Action proof strip

Show:

- predecessor id
- successor id
- requested action: `promote`, `retire`, `promote-and-retire`, `rollback`, `abort`
- proof status: `ready`, `ready-with-debt`, `blocked`, `unknown`
- total covered subjects
- total blocked subjects

### 2) Promotion proof card

Show:

- successor relation class
- covered worlds
- covered field families
- auto-adopt count
- explicit-confirmation count
- pinned/grandfathered count
- blocked count
- strongest safe promotion sentence

## Hard rule

The page may not show `ready` if any subject classified as `unknown` is still inside the requested coverage set.

### 3) Retirement proof card

Show:

- predecessor retirement posture
- remaining live bindings
- remaining predecessor-only waivers
- orphan-risk count
- historical receipt preservation status
- strongest safe retirement sentence

## Hard rule

The page may not offer `retire now` if predecessor-only waivers exist without explicit disposition.

### 4) Subject-outcome card

Publish the final subject outcomes:

- `moves-to-successor`
- `stays-on-predecessor-temporarily`
- `grandfathered-under-deprecated-profile`
- `blocked-until-action`
- `detached-before-retirement`
- `orphaned-if-proceed`
- `rolled-back`

For each outcome show:

- subject count
- representative worlds
- action owner
- next review moment

### 5) Waiver-resolution card

For each waiver cohort show final verdict:

- `resolved`
- `carried-forward`
- `re-prove-required`
- `blocks-retirement`
- `split`
- `expired`
- `unknown`

Also show:

- count by verdict
- owner count
- next rereview date
- unresolved debt headline

### 6) Activation-and-rollback card

Show the change mechanics:

- activation rung for successor currentness
- when predecessor becomes deprecated
- when predecessor becomes retired
- rollback class: `clean`, `partial`, `branch-only`, `receipt-only`, `none`, `unknown`
- rollback prerequisites

## Hard rule

Rollback may never be advertised as `clean` when subjects were detached, orphaned, or moved into narrower world scope.

### 7) Commit receipt

Emit one compact receipt with:

- predecessor id
- successor id
- requested action
- final readiness verdict
- subject outcome counts
- waiver verdict counts
- retirement posture
- rollback class
- strongest safe commit sentence
- blocked stronger sentence

## Copy rules

- Never say `promotion complete` if the predecessor is only deprecated, not retired.
- Never say `retirement complete` if grandfathered subjects remain.
- Never say `fully migrated` if any subject stayed pinned or out of scope.
- Never say `rollback ready` without naming rollback class and prerequisites.
- Never say `no blockers` when the real truth is `no blockers inside the narrowed coverage set`.

## Example strongest-safe sentence patterns

- `Promotion is ready with debt: 842 subjects move to the successor now, 19 are grandfathered under the deprecated predecessor, and predecessor retirement remains blocked on 4 carry-forward waiver decisions.`
- `Retirement is not ready: 6 predecessor-only bindings and 2 unresolved migration-gap waivers would become orphaned if we proceed.`
- `Rollback is branch-only: the predecessor receipts survive, but subjects already detached into the successor branch will not cleanly re-enter live inheritance.`

