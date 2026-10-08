# Instrumentation plan page — capture family, baseline delta, and cost budget interface spec

## Purpose

Give the operator one durable page that answers:

- what diagnostic question justifies changing runtime posture at all
- what the current baseline posture is before any changes
- which capture families or setting deltas are proposed
- what restart, dwell, retention, or privacy costs those deltas carry
- what stronger sentence about evidence sufficiency is still forbidden before activation

This page exists so `turn on debug logging`, `raise log_size`, `enable profiler`, and `drop debug.txt` become a reviewed plan rather than scattered support ritual.

## Inputs

- incident identifier and current hypothesis
- current runtime baseline values and feature availability
- requested capture families (`debug-logging`, `profiler`, `crash-watch`, `anonymous-metrics-only`, `mixed`)
- proposed deltas (`enable`, `increase`, `route override`, `arm on restart`, `leave unchanged`)
- storage/retention budget
- authority/policy constraints
- expected reproduction window or dwell requirement

## Primary questions this page must answer

1. Why is instrumentation being changed for this incident?
2. What is the current baseline posture before the change?
3. Which specific deltas are proposed, and what diagnostic question does each answer?
4. What cost, retention, or privacy consequences come with those deltas?
5. Which deltas must be reviewed together because they interact?

## Layout

### A. Plan strip

Fields:

- incident headline
- plan version
- baseline posture verdict (`baseline`, `already-elevated`, `mixed`, `unknown`)
- proposed capture family summary
- change budget verdict (`light`, `moderate`, `heavy`, `unsafe-without-review`)

### B. Baseline posture card

Show:

- current debug logging state
- current profiler state
- current log-size / retention posture if known
- hidden/advanced enablement already present or absent
- strongest honest baseline sentence
- one stronger forbidden sentence

### C. Proposed deltas table

Columns:

- delta id
- target control or route (`debug-toggle`, `debug.txt`, `log_size`, `profiler_enabled`, `other`)
- before value / state
- proposed after value / state
- diagnostic purpose
- activation mode (`immediate`, `restart-required`, `reproduction-window`, `manual-stop`, `unknown`)
- expected cost (`disk`, `cpu`, `memory`, `privacy`, `operator-attention`)
- review verdict (`approved-candidate`, `needs-scope-narrowing`, `blocked`)

### D. Cost and retention card

Show:

- projected artifact growth
- rotation / TTL expectations
- whether baseline storage or privacy posture materially changes
- whether some deltas should be time-boxed or auto-expire
- whether the incident budget supports the cost

### E. Activation strategy card

Show:

- whether deltas should activate together or in phases
- restart requirements
- minimum dwell after reproduction
- who must witness or approve activation
- next required page: `Instrumentation change review`

## Required interactions

- `Approve proposed delta`
- `Narrow delta scope`
- `Drop delta from plan`
- `Mark baseline as already elevated`
- `Stage activation set`
- `Open instrumentation change review`
- `Defer capture plan`

## Guardrails

- Never treat `include logs later` as equivalent to `instrumentation not changing now`.
- Never hide the current baseline when proposing a temporary delta.
- Never bundle profiler capture, debug logging, and log-size inflation into one vague `diagnostics on` label.
- Never approve a heavier delta without showing what diagnostic claim it buys.
- Never let a hidden route (`debug.txt`, direct config edit) bypass the same review budget as a visible toggle.

## Output

A reviewed instrumentation plan preserving baseline posture, proposed deltas, cost budget, activation ordering, and the diagnostic question each change is meant to answer.
