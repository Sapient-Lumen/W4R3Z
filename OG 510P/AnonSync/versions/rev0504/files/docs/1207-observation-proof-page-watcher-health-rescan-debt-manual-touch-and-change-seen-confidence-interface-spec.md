# Observation proof page — watcher health, rescan debt, manual touch, and change-seen confidence

## Purpose

After any serious `did you actually see my edit?` dispute, a later operator must be able to answer that question without reopening troubleshooting folklore.
This page exists because freshness, chronology, and publication claims all weaken when change observation is weak.

## Proof ladder

### Rung 1 — weak observation

We know only that the file is different now or that an operator says it changed.
We do **not** yet know whether the product saw the change live.

Show:

- current file identity
- operator-claimed change time, if any
- no live event witness
- no completed rediscovery witness yet

Allowed sentence:

- `change reported, product witness still weak`

Blocked stronger sentence:

- `the product observed this edit when it happened`

### Rung 2 — rescan discovery

We know the product found the changed file through periodic or manual rescan.

Show:

- rescan type (`periodic`, `manual`, `startup`)
- discovery time
- current rescan interval and whether it is carrying observation debt
- whether watcher exhaustion or notification loss is active or suspected

Allowed sentence:

- `change rediscovered on rescan`

Blocked stronger sentence:

- `change was seen live`

### Rung 3 — live watcher observation

We know the product received live change notification and attributed the changed path through the normal watcher lane.

Show:

- watcher health for the relevant scope
- event-arrival time
- whether later rescans merely confirmed the event
- whether publication still waited on quiescence or chronology

Allowed sentence:

- `change observed live`

Blocked stronger sentence:

- `change was published immediately and correctly`

### Rung 4 — manual induction

We know the operator used `touch` or an equivalent manual step to force detection.

Show:

- manual act used
- pre-manual witness class
- post-manual witness class
- that manual induction repairs observation but does not prove original event timing

Allowed sentence:

- `change recognition induced manually`

Blocked stronger sentence:

- `manual touch proves when the real edit happened`

## Required side proofs

The page must also show:

- watcher-limit state where relevant
- whether observation currently depends on `folder_rescan_interval`
- whether a zero or changed rescan interval weakens the recovery ladder
- whether a restart was required to restore observation strength

## Compact output

The page must produce:

- `change_seen_confidence` (`weak`, `rescanned`, `live`, `induced`)
- `watcher_health` (`healthy`, `degraded`, `exhausted`, `unknown`)
- `rescan_dependence` (`none`, `periodic`, `manual`, `startup-only`)
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
