# Case closure proof page: resolved, mitigated, unresolved, reopen triggers, and residual risk interface spec

## Purpose

After adjudication and remediation, the archive still needed one explicit page for the final operator question:

> what exact closure class is honest now, what risk still remains, what would reopen this, and what stronger sentence are we still not allowed to say?

## Core decision

AnonSync must expose one first-class **Case closure proof** for every non-trivial case before it can move to `closed` or `watching`.

## Fixed page order

1. **Closure header**
2. **Closure class proof card**
3. **Residual risk card**
4. **Reopen trigger contract**
5. **Watch window and review owner**
6. **Blocked stronger sentence**

### 1) Closure header

Show:

- linked case id
- proposed closure class
- proposer
- reviewer
- decision time
- watch window
- reopen sensitivity

Supported `reopen_sensitivity` values:

- `any-repeat`
- `repeat-same-symptom`
- `repeat-same-hypothesis`
- `repeat-after-same-run`
- `repeat-above-threshold`

### 2) Closure class proof card

The page must support these distinct closure classes:

- `resolved-root-cause-supported`
- `resolved-best-current-explanation`
- `mitigated-not-proven-resolved`
- `workaround-in-place`
- `self-recovered-observed`
- `unknown-but-stable`
- `unresolved-awaiting-external`
- `closed-as-duplicate-or-merged`
- `reopened`

Required rows:

- why this closure class is justified
- why stronger closure classes lost
- what evidence was required
- what evidence was absent
- what symptom sentence is still true
- what cause sentence is safe

Hard rule:

`symptom no longer visible` must never, by itself, justify `resolved-root-cause-supported`.

### 3) Residual risk card

Publish explicit rows for:

- recurrence risk
- data-loss risk
- topology / world-divergence risk
- identity / metadata fragility risk
- operator-confusion risk
- monitoring blind spot risk
- external dependency risk

Supported verdicts:

- `cleared`
- `reduced`
- `unchanged`
- `unknown`
- `heightened-by-workaround`

Also publish one free-text field:

- `most-dangerous-overread`

Example:

- `most-dangerous-overread`: `assuming the reconnect fixed the real cause rather than only re-established current connectivity`

### 4) Reopen trigger contract

Each trigger row must show:

- trigger id
- trigger description
- severity on reopen
- whether reopen is automatic or review-gated
- linked hypothesis to revive
- evidence class expected on reopen

Supported automatic triggers must include:

- `same-warning-reappears`
- `same-run-class-needed-again`
- `same-subject-regresses`
- `same-cause-family-evidence-returns`
- `watch-window-breach`

Supported review-gated triggers must include:

- `similar-symptom-different-scope`
- `new-evidence-undermines-cause-claim`
- `support-feedback-changes-theory`
- `operator-merge-proposal`

### 5) Watch window and review owner

Required fields:

- watch start
- watch end
- what is actively watched
- who reviews breaches
- what evidence is sufficient to let the watch end quietly

Supported watch outcomes:

- `watch-ended-clean`
- `watch-ended-but-risk-persists`
- `reopen-triggered`
- `watch-extended`

### 6) Blocked stronger sentence

This must remain visible even after closure.
Example sentences:

- `we eliminated the root cause` blocked because only mitigation was proven
- `the issue is gone across the whole cohort` blocked because only one subject was rechecked
- `future recurrence is unlikely` blocked because watch window is still open

## Mandatory interaction rules

- Closure cannot publish without at least one blocked stronger sentence.
- The page must preserve which hypotheses remain open even if the case closes as stable.
- Reopen triggers must be machine-comparable where possible, not prose-only.
- If the case merges into another, the old closure proof must point to the successor case rather than vanish.

## Why this page exists

Closure is where products most often lie by accident.
The page exists to keep the archive honest.
