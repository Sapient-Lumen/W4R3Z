# Remediation run contract sheet page: step graph, prerequisites, quiet point, and abort boundary interface spec

## Purpose

The archive already has pages for intervention selection and chosen-action proof.
What it still lacked was one ordinary page for the next operator question:

> now that we chose the next intervention, how exactly do we execute it, in what order, what has to be true before we start, and where are the points where we must stop instead of pressing on?

Current official Resilio docs make this seam concrete because they often describe order-dependent runs — restart before reconnect proof, archive check before deleting `.sync`, service restart after principal switch, restart before debug-log reproduction, rescan cadence constraints after watcher-limit repair — but they do not normalize that into one operator-facing execution object.

## Core decision

AnonSync must expose one first-class **Remediation run contract sheet** whenever a selected intervention has more than one operational step, any destructive boundary, any observer handoff, or any checkpoint whose failure changes what comes next.

The sheet exists to answer ten things in one place:

1. what chosen intervention this run is executing
2. what target sentence the run is trying to unlock
3. what exact ordered steps exist
4. what must be true before step one
5. where quiet points, freeze points, and restart points sit
6. what destructive boundaries exist
7. what checkpoint evidence is required after each critical step
8. what safe-continue rule applies after each checkpoint
9. what safe-abort rule applies if a checkpoint fails
10. what final proof ceiling remains even if the run succeeds

## Fixed page order

1. **Run header**
2. **Preflight gate card**
3. **Step graph**
4. **Checkpoint and witness card**
5. **Abort / rollback boundary card**
6. **Blocked stronger sentence**

### 1) Run header

Show at minimum:

- `run_id`
- linked intervention id
- subject scope
- chosen intervention label
- run class
- target sentence
- current run status
- active operator / handoff owner
- last advanced time

Supported headline statuses must include:

- `drafted`
- `awaiting-preflight`
- `ready-to-start`
- `paused-at-quiet-point`
- `executing`
- `awaiting-checkpoint`
- `safe-to-continue`
- `abort-required`
- `rolled-back`
- `completed-with-partial-proof`
- `completed-with-strongest-available-proof`
- `handed-off`

Supported `run_class` values must include:

- `observe-and-wait`
- `restart-and-verify`
- `rescan-and-verify`
- `reconnect-run`
- `readd-run`
- `environment-repair-run`
- `world-shift-run`
- `artifact-capture-run`
- `mixed-branch-run`

### 2) Preflight gate card

Show explicit rows for at least:

- issue locality
- peer / cohort coordination status
- destination / path intent known
- archive / survivor review completed
- current observer coverage
- restart cost acknowledged
- maintenance window fit
- rescan / notification posture
- current rollback path available
- gating unknowns

Supported gate verdicts must include:

- `clear`
- `clear-with-warning`
- `blocked`
- `not-yet-checked`
- `not-applicable`

Hard rule:

No destructive step may execute while any destructive prerequisite remains `blocked` or `not-yet-checked`.

### 3) Step graph

Each row is one step node in the run.
Required columns:

- `step_id`
- step type
- human description
- predecessor steps
- branch condition
- quiet point requirement
- destructive class
- expected witness
- safe-continue trigger
- safe-abort trigger

Supported `step_type` values must include at least:

- `inspect`
- `freeze`
- `restart`
- `rescan`
- `disconnect`
- `reconnect`
- `remove`
- `readd`
- `delete-service-state`
- `switch-principal`
- `apply-config`
- `raise-system-limit`
- `reproduce-issue`
- `collect-artifacts`
- `wait-window`
- `verify`
- `handoff`
- `rollback`

Rules:

- step order must be explicit, not implied by prose
- branch conditions must be attached to the node that branches, not hidden in a note
- any step that can fork runtime world, storage world, or subject set must be visually stronger than local steps
- more than one future path may be allowed, but only one current path may be active at a time

### 4) Checkpoint and witness card

This card must publish the evidence needed to move past each major step.
Show at minimum:

- checkpoint id
- related step ids
- evidence class
- required freshness window
- pass predicate
- weak-pass predicate
- fail predicate
- manual sign-off requirement

Supported evidence classes must include:

- `ui-state`
- `queue-state`
- `warning-state`
- `history-state`
- `path-state`
- `peer-connectivity-state`
- `artifact-present`
- `restart-completed`
- `operator-confirmation`

Hard rule:

A checkpoint may never publish only `looks better`.
It must bind to a typed pass predicate.

### 5) Abort / rollback boundary card

This card must separate these dimensions explicitly:

- destructive boundary crossed?
- rollback still clean?
- rollback prerequisites still available?
- wrong-destination risk
- archive-loss risk
- world-fork risk
- coordination-loss risk
- proof ceiling after rollback

Supported rollback classes:

- `instant-return`
- `restart-to-return`
- `reconnect-to-return`
- `readd-to-return`
- `new-world-no-clean-merge`
- `unknown`

Supported abort reasons must include:

- `archive-risk-not-cleared`
- `unexpected-world-fork`
- `wrong-destination-proposed`
- `peer-coordination-missing`
- `checkpoint-failed`
- `evidence-stale`
- `unexpected-new-symptom`
- `operator-window-ended`

### 6) Blocked stronger sentence

Always show at least one stronger sentence that remains blocked even if the run completes.
Examples:

- `Sync resumed after restart` may still be weaker than `root cause eliminated`.
- `Folder re-added successfully` may still be weaker than `old local metadata preserved`.
- `Local System workaround restored writes` may still be weaker than `service-world continuity preserved`.
- `Debug logs captured` may still be weaker than `issue explained`.

## Hard rules

- no run may start without a published preflight state
- no destructive node may run without an abort boundary and rollback class
- every restart-bound or wait-window-bound step must publish its observation window explicitly
- every handoff must preserve the next active step, last passed checkpoint, and current strongest safe sentence
- completed runs must distinguish `goal reached` from `evidence collected for stronger action later`

