# Execution readiness review page: preflight, archive risk, observer coverage, and concurrency freeze interface spec

## Purpose

The run contract sheet describes the step graph.
This page exists to decide whether the run is actually safe to start now.

The core question is:

> do we currently have enough preflight truth to start the chosen remediation run, or would starting now turn an otherwise valid intervention into unnecessary damage, ambiguous proof, or unfinishable work?

Current official Resilio docs make this seam concrete because they routinely hide serious preflight concerns in separate places:
archive review before deleting `.sync`, path intent before reconnect, peer coordination before all-peer re-add, restart before logs become meaningful, Local System world shift after service change, and rescan limitations when watcher or rescan posture is unusual.

## Core decision

AnonSync must expose one **Execution readiness review** before any run that:

- crosses a destructive boundary
- requires restart or observation windows
- affects more than one subject or peer
- can fork runtime, service, or storage world
- depends on witness capture to justify the next step

The page decides whether the run is:

- `start-now`
- `start-after-preflight-fix`
- `safe-only-as-observe-run`
- `block-and-replan`

## Fixed page order

1. **Readiness summary**
2. **Preflight checklist matrix**
3. **Archive and survivor review**
4. **Observer coverage and concurrency freeze**
5. **Start / delay / block decision**

### 1) Readiness summary

Show at minimum:

- `readiness_review_id`
- linked run id
- current verdict
- required missing preflight items
- maintenance-window fit
- observer coverage grade
- destructive steps in planned run

Supported verdicts:

- `start-now`
- `start-now-with-watchpoints`
- `delay-for-preflight`
- `observe-only-first`
- `block-and-redesign`

### 2) Preflight checklist matrix

Required rows:

- issue locality understood
- target subjects confirmed
- destination/path intent confirmed
- archive risk checked
- important unsynced survivors checked
- restart authority available
- peer coordination available
- service/config world implications reviewed
- rescan / watcher posture reviewed
- rollback path available
- evidence freshness acceptable

Required columns:

- `item`
- current status
- evidence basis
- operator confidence
- blocking consequence if false
- owner

Supported statuses:

- `confirmed`
- `probable`
- `unknown`
- `negative`
- `not-applicable`

Rules:

- any `unknown` on a destructive prerequisite downgrades the verdict to `delay-for-preflight` or `block-and-redesign`
- any `negative` on rollback availability downgrades world-shift and delete-state runs by default

### 3) Archive and survivor review

This section exists because destructive repair often hides survivor risk.

Show explicit rows for:

- archive contains potentially important data
- local unsynced material may be displaced
- placeholder-only entries may vanish on disconnect
- reconnect default path differs from intended path
- existing directory non-empty collision risk
- old metadata world is intended to survive or not

Supported survivor postures:

- `none-detected`
- `reviewed-and-acceptable`
- `reviewed-and-not-acceptable`
- `still-unknown`

Hard rule:

A run containing `remove`, `readd`, `delete-service-state`, or `switch-principal` cannot receive `start-now` while survivor posture is `still-unknown` or `reviewed-and-not-acceptable`.

### 4) Observer coverage and concurrency freeze

This section answers whether the run can be observed clearly enough to interpret the outcome.

Show at minimum:

- active operator present
- secondary reviewer present when required
- UI/queue/history surfaces available
- warning surface available
- artifact capture lane enabled if needed
- competing changes paused or frozen
- peer communication channel open
- maintenance window end known

Supported coverage grades:

- `strong`
- `adequate`
- `thin`
- `insufficient`

Supported concurrency postures:

- `open`
- `advisory-freeze`
- `hard-freeze`
- `single-operator-window`

Hard rule:

If observer coverage is `thin` or `insufficient`, a run may still proceed only if the declared goal is artifact capture or low-risk observe-only work.

### 5) Start / delay / block decision

This card publishes:

- decision outcome
- exact blockers
- allowed first step
- first forbidden step
- earliest re-review trigger
- stronger sentence still blocked even if the run begins

Example stronger-sentence blocks:

- `safe to start restart` may still be weaker than `safe to start destructive cleanup`
- `safe to capture logs` may still be weaker than `safe to rebuild share state`
- `safe to reconnect one peer` may still be weaker than `safe to run all-peer re-add`

## Hard rules

- this page must exist before the first destructive step in any material run
- archive and path intent must never hide inside freeform notes
- observer coverage must affect the verdict directly
- maintenance-window shortage must be allowed to block otherwise-correct runs
- readiness verdicts must preserve the strongest safe sentence, not just a go/no-go badge

