# Health triage review page: busy-recovering, rescan-only, suspended, and corrupt verdicts

This page exists so the operator can resolve ambiguous `not syncing` complaints into one reviewed health verdict instead of jumping straight to repair rituals.
The product already knows whether warning evidence points toward hidden background work, detection downgrade, external lock, one-subject suspension, or deeper state damage.
That evidence must be assembled before any destructive step is suggested.

## Operator question

> Which health verdict best fits the evidence now, what counter-candidates remain, and what immediate repair rung is justified without overclaiming?

## When this page must appear

Render whenever:

- multiple warnings could explain the same stalled experience
- a subject appears idle but hidden work is still ongoing
- change detection has degraded and the operator expects live arrival
- a blocked path may be lock, permission, or disk failure
- a subject is suspended and the operator needs to know whether reconnect or rebuild is next
- support escalation or destructive repair is being considered

## Fixed page order

1. **Evidence set**
2. **Candidate verdicts**
3. **Winning verdict**
4. **Blocked stronger verdicts**
5. **Immediate next step**

## 1) Evidence set

Show:

- warning rows involved
- observed symptoms: no progress, slow progress, missing arrivals, blocked files, one-subject suspension, crash/restart history, memory pressure
- local witnesses: queue state, file list, lock list, watcher posture, free-space posture, sidecar/database status
- freshness of each witness

The operator must be able to answer: **what evidence is this review actually using?**

## 2) Candidate verdicts

Rank and explain at least these candidates where relevant:

- `busy-but-recovering`
- `degraded-rescan-only`
- `externally-blocked`
- `subject-suspended-db`
- `subject-suspended-sidecar`
- `resource-starved-memory`
- `unknown`

For each candidate show:

- supporting witnesses
- contradictions
- what repair rung it would justify if it won

The operator must be able to answer: **what are the live competing explanations?**

## 3) Winning verdict

Show:

- current winner
- confidence
- affected scope
- sentence the product is allowed to say now

Examples:

- `The subject is degraded into rescan-only detection, not globally stopped.`
- `This subject is suspended because its database cannot be read.`
- `Transfer is blocked by another application, but the runtime spine still appears healthy.`

The operator must be able to answer: **what does the product currently believe is actually wrong?**

## 4) Blocked stronger verdicts

Show the stronger statements that remain blocked, such as:

- `Sync is fully stuck`
- `This is safe to ignore`
- `Deleting sidecar state is already justified`
- `All local state is disposable`
- `Restart alone will definitely fix it`

For each blocked statement show exactly which witness is missing.

The operator must be able to answer: **what are we still refusing to overclaim?**

## 5) Immediate next step

Offer only review-matched next actions:

- `Wait and re-check progress`
- `Trigger rescan / watcher repair`
- `Reveal locked paths`
- `Restart runtime`
- `Reconnect same destination`
- `Prepare destructive rebuild`
- `Capture support logs`

And show whether each action preserves or risks local state.

## What this page must never imply

It must never imply that these are the same:

- no visible transfer and no hidden work
- `not syncing` complaint and spine corruption
- lock symptom and safe re-add
- rescan-only degraded state and live notify parity
- memory pressure and harmless backlog

## Receipt / audit consequence

Opening or completing this review should write a receipt entry that preserves the evidence set, winner, blocked stronger verdicts, and next-step ceiling.
