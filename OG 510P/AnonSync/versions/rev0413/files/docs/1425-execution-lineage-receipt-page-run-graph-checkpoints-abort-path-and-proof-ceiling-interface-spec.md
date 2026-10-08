# Execution lineage receipt page: run graph, checkpoints, abort path, and proof ceiling interface spec

## Purpose

A remediation run needs a durable closing artifact.
This page exists to preserve what run was attempted, what checkpoints passed, what boundaries were crossed, and what the strongest surviving claim actually is.

The core question is:

> after this remediation run, what exactly happened, what remains true, what stronger sentence is still blocked, and what next action would be justified if work resumes?

## Core decision

AnonSync must emit one **Execution lineage receipt** whenever a material remediation run stops for any reason: success, partial success, abort, rollback, or handoff closure.

## Fixed page order

1. **Receipt header**
2. **Executed run graph summary**
3. **Checkpoint outcome summary**
4. **Abort / rollback summary**
5. **Final proof ceiling and next action**

### 1) Receipt header

Show at minimum:

- `execution_receipt_id`
- linked run id
- linked intervention id
- closure type
- closed time
- closing operator
- subject scope

Supported closure types:

- `completed-strong`
- `completed-partial`
- `aborted`
- `rolled-back`
- `handed-off-closed`
- `superseded-by-new-run`

### 2) Executed run graph summary

Show:

- planned steps total
- executed steps total
- skipped steps total
- branch actually taken
- highest destructive class reached
- world-fork occurred?
- last clean rollback class preserved

### 3) Checkpoint outcome summary

Show a compact table with:

- checkpoint id
- verdict
- witness basis
- freshness at verdict time
- stronger sentence unlocked
- stronger sentence still blocked

Hard rule:

Weak passes must remain visible forever.
A future reader should not have to guess which truths were provisional.

### 4) Abort / rollback summary

Show explicit rows for:

- abort triggers encountered
- rollback attempted or not
- rollback class actually used
- irreversible boundaries crossed
- data / metadata survivor caveats
- path continuity caveats
- operator-window caveats

Supported irreversible-boundary labels:

- `none`
- `metadata-rebuilt`
- `subject-detached`
- `subject-readded`
- `service-world-replaced`
- `settings-world-rebased`
- `unknown`

### 5) Final proof ceiling and next action

This card must publish three sentences:

- strongest safe sentence now
- strongest stronger sentence still blocked
- next justified action if work resumes

Supported next-action classes:

- `observe-only`
- `resume-same-run`
- `start-stronger-intervention`
- `start-artifact-run`
- `human-escalation`
- `no-further-action-justified`

## Hard rules

- the receipt must stand on its own without requiring the live run page
- it must preserve both irreversible changes and surviving clean reversibility
- it must never confuse `completed the run` with `proved root cause removed`
- it must always name the next justified action class, even if that class is `no-further-action-justified`

