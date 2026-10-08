# Health lineage receipt page: warning basis, repair rung, and state-loss boundary

This page exists so later operators do not have to rediscover why a warning mattered, why a certain repair rung was chosen, or which survivors were expected.
Health work is not done when the badge disappears.
The product needs one durable receipt that preserves what kind of failure this was and what continuity or destruction boundary the operator accepted.

## Operator question

> What health problem was diagnosed, what repair rung was actually crossed, what state-loss or salvage boundary was accepted, and what stronger sentence remained blocked afterward?

## When this receipt must be written

Write it whenever the operator:

- completes health triage
- crosses any repair rung stronger than `observe-only`
- captures logs for escalation
- deletes or recreates a state spine
- performs a coordinated re-add / re-share
- accepts a degraded-but-usable state instead of full recovery

## Fixed receipt fields

### 1) Warning basis

Record:

- original warning / symptom ids
- affected scope
- winning health verdict
- freshness of evidence used

### 2) Repair rung crossed

Record:

- chosen rung
- whether weaker rungs were attempted first
- whether the rung was vendor-documented, product-inferred, or support-directed

### 3) Survivor and loss boundary

Record:

- archive/history survivor expectation
- sidecar/database survivor expectation
- local-only byte risk accepted
- partial-download residue handled or deferred
- peer coordination requirement accepted or not

### 4) Post-repair proof ceiling

Record:

- strongest proven sentence after the rung
- blocked stronger sentence
- watch / escalation expiry or reopen trigger

### 5) External escalation package

If support escalation occurred or remains likely, record:

- logs captured
- devices / subjects included
- whether any destructive step happened before capture

## Receipt summary sentence

The top summary must read like this:

> `Subject suspended by database corruption; local reconnect was attempted first; later re-add was chosen after archive review; hidden history survival remained operator-reviewed; post-repair state recovered transfer but not yet full live-observation proof.`

## What this receipt must never flatten

It must never flatten these into one vague `repaired` note:

- intermittent background work vs corruption
- degraded rescan-only detection vs full recovery
- restart vs reconnect vs re-add
- sidecar recreation vs harmless retry
- evidence capture before repair vs after destructive mutation

## Audit / later-action consequence

Later pages that propose the next rung, a closure decision, or a support handoff must import this receipt directly instead of re-asking the operator to remember the sequence.
