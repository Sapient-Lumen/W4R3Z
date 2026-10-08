# Signal-adjudication review page: warnings, history, graphs, logs, and human escalation interface spec

## Purpose

The rollout-health contract sheet summarizes the current judgment.
The **Signal-adjudication review** is the deeper working page where the operator compares the evidence planes that produced that judgment.

It exists because current Resilio material still teaches operators to hop among live graphs, warnings, history, queue views, troubleshooting KB pages, and log collection flows.
AnonSync should make the joins explicit.

## Core operator question

> are these symptoms real, fresh, and rollout-relevant enough to stop or slow promotion, or are we looking at transient noise, host pressure, stale artifacts, or unresolved ambiguity?

## Fixed page order

1. **Evidence-plane matrix**
2. **Signal conflict review**
3. **Escalation-artifact review**
4. **Decision outcome strip**

### 1) Evidence-plane matrix

Rows must include at least:

- live metric plane
- warning/status plane
- history/event plane
- queue/peer plane
- support-artifact plane
- known-issue plane
- operator-note plane

Columns must include at least:

- freshness
- cohort coverage
- observed severity
- causal strength
- rollout relevance
- contradictions
- adjudication status

### 2) Signal conflict review

The page must force explicit handling of conflict cases such as:

- graph looks green while warnings persist
- warnings clear while queue debt remains
- logs show repeated error while live metrics look normal
- known issue prior exists but local reproduction is weak
- operator report is severe but artifact freshness is stale

Supported conflict outcomes must include:

- `metric-over-warning`
- `warning-over-metric`
- `artifact-over-surface`
- `surface-over-artifact`
- `conflict-unresolved`
- `mixed`

### 3) Escalation-artifact review

Separate these artifact classes explicitly:

- debug log bundle
- profiler trace
- crash dump / mini dump
- support narrative
- forum or community precedent
- internal operator note

Each artifact row must show:

- capture time
- reproduction basis
- whether restart or repro step preceded capture
- whether the artifact is directly promotable to product truth
- required human adjudication level

Supported artifact-verdict classes must include:

- `usable-now`
- `usable-with-caveat`
- `stale-artifact`
- `captured-without-repro`
- `needs-recapture`
- `not-decision-grade`

### 4) Decision outcome strip

The page must end with one explicit decision strip containing:

- `proceed`
- `proceed-guarded`
- `hold-for-fresh-artifacts`
- `freeze-promotion`
- `rollback-ring`
- `unknown`

And it must show:

- why this outcome won
- which rival outcomes were rejected
- what evidence would change the answer fastest

## Hard rules

- `needs more logs` is not a complete decision; the rollout consequence must still be explicit
- forum/community evidence must never outrank fresh cohort evidence without explanation
- artifacts captured without a clear reproduction basis must be visibly weaker
- one evidence plane clearing up must not erase unresolved conflicts in another plane
