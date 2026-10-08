# Local fault recovery ladder and copy-safety interface spec

## Purpose

The archive already had repair ladders and diagnostics language.
What it still lacked was one explicit interface contract for the ordinary class of local faults that current sync tools still resolve with restart, reconnect, touch-files, or remove-and-readd folklore:

> when one seat is locally unhealthy, what is the least-destructive repair step, what evidence justifies climbing to the next step, and what local-copy risk comes with each rung?

Current Resilio docs make this seam concrete.
Their current locked-files doc still says Sync cannot identify the locking application, advises manual investigation, and falls back to restart.
Their current `My files don't sync` doc still sends operators toward restart, touching files, deleting stuck `.!sync` artifacts after restart, or re-adding a folder when trees cannot merge.
Their current database-error doc still escalates from restart to disconnect/reconnect and then to remove/re-add on all peers if needed.

That means repair severity is still described mostly as troubleshooting prose, not one typed recovery ladder with copy-safety truth.

## Core decision

AnonSync must expose one **fault recovery ladder** per incident.
Every rung must say:

- what evidence justified this rung
- what local-copy and receipt risk it carries
- what stronger proof is gained if it succeeds
- what broader blast radius the next rung would impose

## Why this matters

Current Resilio behavior still spreads recovery truth across separate pages:

- `restart` is a frequent first response
- `reconnect to same destination` can rebuild only local database state
- `delete partial residue` is another special-case ritual
- `remove and re-add` can become the broad fallback for merge or database trouble

AnonSync should therefore hold one stronger rule:

> every escalation step must preserve the strongest honest statement about local bytes before it asks the operator to risk them.

## Fixed review order

Every repair flow should render the same sections in the same order:

1. **Observed fault**
2. **Least-destructive next rung**
3. **Escalation ladder**
4. **Local-copy / residue safety**
5. **Repair receipt**

### 1) Observed fault

Classify the incident as one or more of:

- `locked local writer`
- `notification gap / stale scan`
- `staged-transfer residue`
- `local database fault`
- `tree-merge fault`
- `permission denial`
- `other reviewed fault`

### 2) Least-destructive next rung

Good first rungs include:

- refresh observation only
- retry without restart
- restart engine/runtime
- re-open watcher / re-scan boundary
- reconnect same subject to same destination without widening scope

### 3) Escalation ladder

Render a fixed ladder such as:

1. observe only
2. retry
3. restart runtime
4. rebuild local ephemeral state
5. clear staged residue only
6. reconnect same subject to same destination
7. reindex subject
8. remove/re-add with reviewed continuity receipt

The product may skip unavailable rungs, but it must never hide them.

### 4) Local-copy / residue safety

For each rung show:

- local bytes preserved, untouched, maybe replaced, or at risk
- placeholders / staged artifacts affected
- receipts preserved vs regenerated
- whether peer-wide action is required
- whether pre-repair local snapshot is recommended

The operator must be able to answer:

> what am I about to fix, and what local evidence or bytes could I lose by climbing one rung higher?

### 5) Repair receipt

The receipt must preserve:

- incident class
- rung attempted
- copy-safety statement shown
- evidence before and after
- whether escalation stopped, succeeded, or broadened to peer-wide action

## Main surface

Every incident page should show one ladder with the current rung highlighted and later rungs visibly more destructive.

A good summary line reads like:

- `Runtime restart may clear the lock symptom without touching subject bytes.`
- `Reconnect will rebuild local ephemeral state against the same destination.`
- `Remove/re-add is peer-wide and requires continuity review before apply.`

## Acceptance criteria

This spec is satisfied when:

- restart/reconnect/re-add are exposed as ordered rungs instead of folklore
- local-copy risk is always stated before destructive repair
- partial-residue cleanup is separated from broader subject rebuild
- successful low rungs end the incident without nudging the operator upward anyway
