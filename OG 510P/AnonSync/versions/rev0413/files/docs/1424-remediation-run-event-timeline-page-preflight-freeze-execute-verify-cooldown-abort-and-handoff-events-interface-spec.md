# Remediation run event timeline page: preflight, freeze, execute, verify, cooldown, abort, and handoff events interface spec

## Purpose

The contract sheet describes the run.
The checkpoint page governs the current step.
This timeline exists to preserve the run as history that another operator can understand without replaying chat, memory, or support folklore.

The core question is:

> what exactly happened during this remediation run, in what order, with what pauses, with what checkpoint outcomes, and where did the run stop, succeed, fork, or get handed off?

## Core decision

AnonSync must expose one **Remediation run event timeline** for any run that crosses more than one step or any notable boundary.

It is not just an audit log.
It is the continuity surface for later reasoning.

## Fixed page order

1. **Timeline summary**
2. **Event stream**
3. **Boundary crossings**
4. **Cooldown / wait windows**
5. **Handoff and reopen section**

### 1) Timeline summary

Show at minimum:

- run id
- start time
- latest event time
- current state
- total boundary crossings
- current step phase
- last safe sentence change

Supported phases:

- `preflight`
- `freeze`
- `execute`
- `verify`
- `cooldown`
- `abort`
- `rollback`
- `handoff`
- `closed`

### 2) Event stream

Each event row must show:

- timestamp
- phase
- event type
- actor
- summary sentence
- affected subjects
- linked checkpoint if any
- resulting strongest safe sentence

Supported `event_type` values must include at least:

- `preflight-cleared`
- `preflight-blocked`
- `freeze-started`
- `freeze-lifted`
- `step-started`
- `step-completed`
- `restart-finished`
- `wait-window-started`
- `wait-window-finished`
- `checkpoint-passed-weak`
- `checkpoint-passed-strong`
- `checkpoint-failed`
- `abort-triggered`
- `rollback-started`
- `rollback-finished`
- `handoff-issued`
- `run-reopened`
- `run-closed`

### 3) Boundary crossings

This section must separately highlight events where the run crossed:

- destructive-cleanup boundary
- disconnect/remove boundary
- re-add boundary
- world-switch boundary
- observer-loss boundary
- proof-ceiling downgrade

For each crossing show:

- boundary type
- crossing time
- last clean rollback class before crossing
- new rollback class after crossing
- stronger sentence permanently lost or still preserved

### 4) Cooldown / wait windows

This section publishes pauses that matter.
Show explicit rows for:

- reason for wait
- minimum duration
- earliest allowed next step
- observer requirements during wait
- what would count as self-recovery versus escalation

Supported wait reasons:

- `post-restart-stabilization`
- `artifact-capture-window`
- `self-recovery-observation`
- `peer-rejoin-window`
- `manual-review-gap`

### 5) Handoff and reopen section

This section exists because many runs continue later.
Show at minimum:

- outgoing operator
- incoming operator
- handoff note
- active step when handed off
- last passed checkpoint
- next allowed action
- next forbidden action
- reopen condition

Hard rule:

A handed-off run must be resumable from this page alone without assuming hidden oral context.

## Hard rules

- timeline order must be immutable once events are written
- summary sentences must preserve the strongest safe sentence at each stage
- cooldown periods are first-class events, not missing activity
- abort and rollback events must never be collapsed into generic failure
- handoff must preserve both what may happen next and what must not happen next

