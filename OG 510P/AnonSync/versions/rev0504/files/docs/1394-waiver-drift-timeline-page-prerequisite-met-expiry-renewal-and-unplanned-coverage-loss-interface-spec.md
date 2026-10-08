# Waiver drift timeline page — prerequisite met, expiry, renewal, and unplanned coverage loss

## Purpose

This page answers the history question that active waiver state alone does not finish:

> how did this exception arise, when should it have ended, what changed while it stayed open, and did the profile silently lose or regain coverage over time?

## Core decision

Every serious exception family must render one first-class **Waiver drift timeline**.
The page owns:

- origin event
- renewal history
- expiry history
- retirement attempts
- unplanned coverage loss
- blocked stronger sentence over time

## Fixed page order

1. timeline summary strip
2. origin event ledger
3. waiver-life event ledger
4. coverage-loss and recovery ledger
5. current debt posture card
6. timeline receipt

### 1) Timeline summary strip

Show:

- waiver id
- profile id
- affected subject/cohort
- issue date
- current age
- current status
- total renewals
- total missed rereviews
- top question being answered: `how did this waiver evolve?`

### 2) Origin event ledger

Record the event that first caused the exception, such as:

- subject entered unsupported world
- field discovered ignored by runtime
- mobile-local lane took over
- prerequisite became missing
- config/service world fork occurred
- successor identity replaced prior world
- profile scope changed and exposed the gap

### 3) Waiver-life event ledger

Record every governance event:

- waiver proposed
- waiver approved
- waiver renewed
- waiver expired
- waiver rereviewed
- waiver denied
- waiver satisfied
- waiver converted to hard out-of-policy

For each event show:

- who acted
- what evidence existed
- what stronger sentence remained blocked afterward

### 4) Coverage-loss and recovery ledger

Keep profile-coverage changes visibly separate from waiver paperwork:

- product support widened
- support narrowed
- field moved surfaces
- migration completed
- local-only lane retired
- stronger evidence proved effect
- previous assumption collapsed

### 5) Current debt posture card

Summarize the present state:

- active or expired
- oldest unresolved blocker
- next required action
- whether rollout remains blocked
- whether the waiver now looks stale, justified, or misclassified

### 6) Timeline receipt

Emit one compact receipt with:

- waiver id
- profile id
- subject/cohort id
- age
- renewal count
- missed-rereview count
- current posture
- strongest safe timeline sentence
- blocked stronger sentence

## Copy rules

- Never let renewal history disappear once the waiver is retired.
- Never treat expiry as a no-op.
- Never let product-support changes masquerade as operator review.
- Never say `still exceptional` without showing how long and why.
- Never let coverage regain count as automatic conformance without recheck.

## Example strongest-safe sentence patterns

- `This waiver began as a migration-gap exception during service cutover, expired once without rereview, and remains active only because successor-world rebind proof is still missing.`
- `The ignored-runtime exception is now likely stale because the supporting product limitation was removed two revisions ago but no recheck has been recorded.`
- `Profile coverage narrowed after the subject moved into an unsupported world; the waiver now reflects a scope change rather than a temporary hold.`
- `The subject regained eligibility after the prerequisite was met, but conformance is still unproven until retirement review completes.`
