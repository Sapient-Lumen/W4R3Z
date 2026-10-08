# Decision portfolio timeline page: promotion, deferral, preemption, and stale-watch events interface spec

## Purpose

Portfolio ordering is rarely one moment.
The operator needs a timeline that answers:

> when did a candidate rise, when was it held back, when did another item preempt it, and when did a watch posture turn into neglect?

## Timeline event types

Supported `portfolio_event_type` values:

- `candidate-added`
- `candidate-removed`
- `promoted-to-now`
- `demoted-to-later`
- `entered-watch`
- `hold-imposed`
- `budget-exhausted`
- `dispatch-fired`
- `preemption-armed`
- `preemption-fired`
- `watch-aging`
- `starvation-breach`
- `forced-review-fired`
- `portfolio-frozen`
- `portfolio-reopened`

## Required columns

- event time
- candidate id
- prior lane
- new lane
- triggering factor or evidence
- displaced candidate if any
- attention-budget delta
- stronger sentence gained or lost
- owner after event

## Hard rules

### Promotion and demotion must name the cause

A transition from `watch` to `now`, or from `now` to `hold`, must name the exact evidence, deadline, capacity shift, or competing pressure that changed the lane.

### Preemption must preserve the losing work

If one candidate preempts another, the timeline must show:

- what was displaced
- whether work stopped, handed off, or safely paused
- what stronger sentence the displaced item lost

### Starvation breach must weaken something concrete

A starvation event must say which previous comfort sentence failed.
For example, `safe to keep watching` must become false in a named way.
