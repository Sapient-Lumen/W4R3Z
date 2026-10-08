# Execution review page — who may carry out which effect and under what supervision

## Purpose

This page is the operator review surface for deciding what execution sentence is honestly earned for a given act version.
It exists so the product can review lower agency rungs and stronger blocked rungs without collapsing them into a single approval story.

## Core questions

The review must let the operator answer all of the following without leaving the page:

- who may execute the current typed effect at all
- whether execution must be by a named human, a delegate, or a supervised agent
- whether linked-device or owner convenience is relevant but still too weak
- whether the act may run automatically or only after a fresh execute-now confirmation
- what supervision or dual control is required
- which stronger agency sentence remains blocked and why

## Mandatory review routes

### Route 1 — Human execution route

Use when the act must be carried out by a named person.
Expose separately:

- principal execution authorized
- principal execution pending fresh confirmation
- principal absent but delegate available
- principal identity ambiguous
- principal execution challenged
- principal-only execution blocked by supersession or correction

### Route 2 — Delegation route

Use when a representative may execute on another's behalf.
Expose separately:

- delegate execution authorized
- delegate authority scope too narrow
- delegate authority stale or expired
- delegate requires countersign
- delegate execution contested by principal
- delegate execution blocked for irreversible effect

### Route 3 — Agent-and-device route

Use when a device, software agent, or automation path is in view.
Expose separately:

- supervised agent may execute
- supervised agent may prepare but not commit
- linked device may route but not execute
- device-only actor present but too weak
- unsupervised autopilot explicitly allowed
- unsupervised autopilot explicitly blocked

### Route 4 — Freshness-and-trigger route

Use when prior assent or standing mandate exists.
Expose separately:

- standing mandate sufficient
- execute-now confirmation required
- execute-now confirmation received
- prior assent stale after correction
- mandate expired by time or role change
- replay attempt blocked

### Route 5 — Supervision-and-rollback route

Use when execution risk or irreversibility is material.
Expose separately:

- single actor enough
- dual control required
- human preview required before final commit
- automatic start allowed but final release manual
- rollback available within window
- rollback impossible so stronger controls required

## Required comparisons

The review must keep these comparisons explicit:

- `agreed in principle` vs `may execute now`
- `principal execution` vs `delegate execution`
- `delegate execution` vs `supervised agent execution`
- `supervised agent execution` vs `unsupervised autopilot`
- `standing mandate` vs `fresh execute-now confirmation`

## Required badges

- `execution-pending`
- `principal-authorized`
- `delegate-authorized`
- `agent-supervised`
- `device-too-weak`
- `autopilot-allowed`
- `autopilot-blocked`
- `fresh-execute-now-required`
- `dual-control-required`
- `execution-effect-blocked`

## Failure modes the page must prevent

- collapsing assent and execution into one step
- letting linked-device owner convenience quietly erase who may actually carry out the act
- mistaking API or automation presence for permission to run an irreversible effect
- forgetting that a lower agency rung may still coexist with a blocked stronger autopilot sentence
- forgetting that supervision requirements may differ by effect even when the actor identity stays the same

## Stronger-sentence guard

The review may say `the named principal assented earlier, a delegate may prepare the payment route, a supervised agent may draft but not send the final execution, and unsupervised autopilot remains blocked pending execute-now confirmation`.
It may not say `the act is cleared for autonomous execution` unless the exact mandate threshold is truly met.
