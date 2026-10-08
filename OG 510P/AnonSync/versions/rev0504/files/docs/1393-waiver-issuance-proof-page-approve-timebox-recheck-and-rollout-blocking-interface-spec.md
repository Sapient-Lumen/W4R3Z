# Waiver issuance proof page — approve, timebox, recheck, and rollout blocking

## Purpose

This page answers the pre-approval question that a waiver summary alone does not finish:

> should this exception actually be granted, how long is it allowed to live, what condition retires it, and does rollout stop here or proceed around the subject?

## Core decision

Every serious exception grant, renewal, or conversion must render one first-class **Waiver issuance proof** before commit.
The page owns:

- grant basis
- timebox
- owner
- retirement trigger
- rollout consequence
- blocked stronger sentence

## Fixed page order

1. issuance strip
2. trigger-and-basis card
3. timebox-and-owner card
4. retirement-trigger card
5. rollout-consequence card
6. issuance receipt

### 1) Issuance strip

Show:

- waiver id or proposed waiver draft id
- profile id and revision
- target subject/cohort
- requested class
- requested duration
- requested owner
- top question being answered: `should this waiver exist at all?`

### 2) Trigger-and-basis card

Show why the waiver is being requested:

- observed divergence
- evidence supporting the divergence
- why ordinary conformance is blocked
- why simple exclusion is insufficient
- whether the divergence is expected, accidental, or still unknown

## Hard rule

A waiver may not be issued from a free-form note alone.
The page must show at least one explicit basis: unsupported world, ignored runtime, local lane, missing prerequisite, migration gap, temporary hold, or evidence gap.

### 3) Timebox-and-owner card

Require:

- explicit owner
- issue time
- expiry or next rereview
- renewal policy
- maximum allowed age under current risk class

## Hard rule

No waiver without an owner.
No indefinite waiver without stronger approval class and rationale.

### 4) Retirement-trigger card

Show the exact event that would let the waiver end:

- prerequisite fulfilled
- migration complete
- world rejoined
- stronger evidence collected
- product support widened
- policy changed
- explicit decision to mark hard out-of-policy

Also show what verification step must happen before retirement is accepted.

### 5) Rollout-consequence card

Show the effect on the pending change:

- `rollout blocked`
- `rollout proceeds around waived subject`
- `rollout allowed for unaffected fields only`
- `rollout postponed pending rereview`
- `no rollout in scope`

For each outcome show:

- value changes allowed
- governance changes allowed
- follow-up review duty

### 6) Issuance receipt

Emit one compact receipt with:

- waiver id
- profile id
- profile revision
- subject/cohort id
- exception class
- owner
- expiry / rereview
- rollout consequence
- strongest safe issuance sentence
- blocked stronger sentence

## Copy rules

- Never say `approved for now` without a timebox.
- Never say `we'll remember` instead of naming owner and rereview.
- Never say `doesn't matter for rollout` without publishing whether values, governance, or both are excluded.
- Never issue a waiver just because the current values happen to match.
- Never let `unsupported` and `temporarily postponed` share the same approval language.

## Example strongest-safe sentence patterns

- `The requested waiver is approved as a 30-day migration-gap exception owned by the service cutover operator; rollout proceeds around the successor world until rebind proof is completed.`
- `This exception is granted only for the ignored-runtime field and does not excuse the rest of the profile from conformance review.`
- `The waiver is denied because the divergence is actually hard out-of-policy rather than temporarily blocked by a prerequisite.`
- `The product cannot approve this waiver yet because the evidence only proves a mismatch, not the correct exception class.`
