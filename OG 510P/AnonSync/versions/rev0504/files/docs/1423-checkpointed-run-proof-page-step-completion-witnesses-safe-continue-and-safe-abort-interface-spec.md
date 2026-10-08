# Checkpointed run proof page: step completion, witnesses, safe continue, and safe abort interface spec

## Purpose

A remediation run should not rely on operator memory between steps.
This page exists to publish the live checkpoint logic as the run unfolds.

The core question is:

> which steps are actually complete, what evidence proves that, is it safe to continue to the next step, and if not, do we pause, abort, or roll back?

Current official Resilio docs make this seam concrete because they describe many runs with intermediate proof needs: restart before logs count, reconnect to same destination, review Archive before deleting `.sync`, restart after watcher-limit change, and re-add only after prior disconnect/remove conditions are met.

## Core decision

AnonSync must expose one **Checkpointed run proof** for any run that:

- contains more than one meaningful step
- can branch based on what is observed mid-run
- can still abort cleanly after some steps but not others
- produces weaker or stronger proof depending on where the run stops

## Fixed page order

1. **Checkpoint summary rail**
2. **Live checkpoint table**
3. **Safe-continue decision card**
4. **Safe-abort / rollback decision card**
5. **Resulting sentence ladder**

### 1) Checkpoint summary rail

Show at minimum:

- total checkpoints
- last passed checkpoint
- current active checkpoint
- last witness time
- current continuation verdict
- current abort posture

Supported continuation verdicts:

- `continue-now`
- `continue-after-wait-window`
- `pause-for-human-review`
- `abort-now`
- `rollback-now`
- `handoff-now`

### 2) Live checkpoint table

Required columns:

- `checkpoint_id`
- related step ids
- expected witness class
- actual witness observed
- freshness
- verdict
- next allowed action
- next forbidden action

Supported verdicts:

- `passed-strong`
- `passed-weak`
- `not-yet-met`
- `failed`
- `superseded`
- `not-applicable`

Rules:

- `passed-weak` must still identify the stronger sentence that remains blocked
- a checkpoint may not be marked `passed-strong` by operator intuition alone when a typed witness was required
- one failed checkpoint may invalidate later planned checkpoints; the page must say so explicitly

### 3) Safe-continue decision card

This card must publish:

- why continuing is currently allowed
- what witness justifies continuation
- which stronger action remains forbidden
- required cooldown or wait window before the next action
- whether additional observer sign-off is required

Supported continue rationales:

- `restart completed and expected state observed`
- `path intent confirmed`
- `archive risk cleared`
- `peer coordination confirmed`
- `artifact capture active`
- `warning cleared but cause still uncertain`
- `environment prerequisite now satisfied`

### 4) Safe-abort / rollback decision card

This card must publish:

- abort trigger observed
- rollback class still available
- required rollback step
- proof ceiling after abort/rollback
- whether the run can be resumed later or must be redesigned

Supported abort outcomes:

- `abort-and-freeze`
- `abort-and-rollback`
- `abort-and-handoff`
- `abort-and-escalate`
- `abort-and-replan`

Hard rule:

Once the run crosses a boundary labeled `new-world-no-clean-merge`, the card must stop using the word `rollback` unless a real merge-safe return path is still proven.

### 5) Resulting sentence ladder

Show at least three rows:

- strongest currently safe sentence
- stronger sentence unlocked only if the next checkpoint passes
- strongest sentence permanently blocked by the current path

Example:

- `Debug logging is definitely active and issue repro has begun`
- `Useful logs covering 15 minutes after repro will exist if the wait window completes`
- `Root cause is known` remains blocked

## Hard rules

- every checkpoint must attach to one or more specific steps
- freshness must be visible when evidence is time-sensitive
- continue/abort language must be explicit and imperative
- handoff must preserve the active checkpoint and forbidden-next-step state
- the page must remember weak passes instead of flattening them into success

