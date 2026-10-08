# Health warning contract sheet page: pressure, lock, spine, and repair class

This page exists so `warning`, `error`, `slow`, and `not syncing` stop pretending to mean the same thing.
A sync subject may be busy but recovering, degraded into rescan-only observation, blocked by another process, suspended because its state spine is damaged, or headed toward a destructive rebuild rung.
One page must declare which health class the operator is actually facing.

## Operator question

> What kind of health problem is this, how severe is it right now, what object is affected, and what repair rung is even on the table?

## When this page must appear

Render this page whenever the product detects or the operator opens:

- a warning or error attached to a subject or runtime
- prolonged hidden work or slow progress with unclear severity
- watcher exhaustion or degraded change detection
- lock contention or blocked transfer
- database / sidecar / service-file corruption
- memory pressure or destructive-rebuild guidance
- a `not syncing` complaint with multiple plausible causes

## Fixed page order

1. **Affected object and blast radius**
2. **Health class**
3. **Detection / transfer / spine truth**
4. **Current repair ceiling**
5. **Salvage obligations**
6. **Receipt promise**

## 1) Affected object and blast radius

Show:

- affected scope: `single-file`, `single-subject`, `subject-tree`, `runtime-wide`, `identity-wide`, `unknown`
- affected object id(s)
- whether other subjects are continuing normally
- whether publication, arrival, or observation is the damaged lane

The operator must be able to answer: **what exactly is unhealthy, and what is still healthy?**

## 2) Health class

Show one primary verdict:

- `busy-but-recovering`
- `degraded-rescan-only`
- `externally-blocked`
- `subject-suspended`
- `spine-corrupt`
- `resource-starved`
- `unknown-health-state`

And show:

- confidence for that verdict
- strongest safe sentence currently allowed
- stronger forbidden sentence if the product has not proven it

The operator must be able to answer: **is this slowdown, degraded detection, a local blocker, a suspension, or corruption?**

## 3) Detection / transfer / spine truth

Show:

- live-watcher posture: `live`, `rescan-only`, `unknown`
- transfer posture: `moving`, `blocked-by-lock`, `blocked-by-space`, `blocked-by-permission`, `not-applicable`, `unknown`
- state-spine posture: `healthy`, `database-corrupt`, `service-files-missing`, `memory-pressure-only`, `unknown`
- whether the runtime itself admits intermittent recovery

The operator must be able to answer: **which lane is actually broken?**

## 4) Current repair ceiling

Show the strongest repair rung currently justified:

- `observe-only`
- `restart-runtime`
- `close-locking-app`
- `increase-watcher-budget`
- `reconnect-same-destination`
- `re-add-subject`
- `delete-sidecar-and-recreate-instance`
- `re-share-biggest-subjects`
- `support-escalation`
- `unknown`

Also show which stronger rungs are still blocked because proof is missing.

The operator must be able to answer: **what is the strongest repair move I can justify right now without guessing?**

## 5) Salvage obligations

Show before any destructive repair:

- archive / hidden history obligations
- partial-download residue that may need review
- local-only bytes or unsent changes at risk
- support-log capture recommendation before mutation
- survivor expectation after the chosen rung

The operator must be able to answer: **what must I preserve or inspect before I escalate?**

## 6) Receipt promise

Show:

- the receipt id that will be written
- what the receipt will preserve about health class, repair rung, salvage duty, and blocked stronger sentence
- which later observation should reopen this contract automatically

## Primary actions

Use only actions that match the reviewed truth.
Examples:

- `Keep observing`
- `Restart and reassess`
- `Open locking-path list`
- `Raise watcher budget`
- `Reconnect same destination`
- `Prepare destructive rebuild`
- `Capture logs before repair`

Do not use vague primaries such as `Fix now`, `Reset Sync`, or `Repair everything` unless the product has actually proven that stronger sentence.

## What this page must never imply

It must never imply that these are the same:

- intermittent background work and corruption
- rescan-only degraded detection and healthy live observation
- local lock contention and state-spine damage
- folder-scoped suspension and runtime-wide failure
- destructive rebuild guidance and harmless retry

## CLI projection expectation

A headless projection such as `anonsync health show --view contract` must render the same sections and verdicts without requiring GUI-only nuance.
