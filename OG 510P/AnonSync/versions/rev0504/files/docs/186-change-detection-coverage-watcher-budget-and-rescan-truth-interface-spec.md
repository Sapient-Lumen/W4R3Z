# Change-detection coverage, watcher budget, and rescan truth interface spec

## Purpose

The archive already had degraded-target semantics, quiescence, and convergence evidence.
What it still lacked was one interface contract for a simpler but more common lie:

> when the product says a folder is `watching for changes`, what page proves whether it is actually running on immediate notifications, periodic rescans, manual rescans, or a half-broken mix of all three?

Current official Resilio docs make this seam much clearer than a generic `sync delay` complaint would.
They still say Sync relies first on filesystem notifications, warn that those notifications have limitations or may not work for some storages such as NFS, SMB2, or deeply nested trees on Windows, and describe a scheduled folder scan that runs every 600 seconds by default and at Sync start.
They also still say the automatic rescan interval can be changed, including to zero, in which case Sync does not rescan folders at all, even on restart.
A separate current warning page still says Linux systems can run out of inotify watchers, that large trees can consume one watcher per subdirectory, and that once the watcher limit is hit Sync learns about updates only through manual or periodic rescans until the system limit is raised and Sync restarted.

That is candid support guidance.
It is still not a good public runtime contract.

## Core decision

AnonSync should make **change-detection coverage** first-class and continuously visible.

Every bind or subject surface that depends on local scanning must always declare:

- the active detection mode
- the expected latency class
- the current watcher or observer coverage
- the current fallback path
- whether `healthy now` depends on a future periodic rescan
- what operator action would improve the situation

If an operator still has to infer coverage from a delayed upload, a Linux sysctl article, or whether a manual rescan fixed it, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal six truths AnonSync should not clone:

- `real-time` can silently mean `best effort if notifications happen to work`
- target class matters to detection semantics, not just to performance
- deep trees and watcher budgets can change update latency from immediate to periodic
- a `zero` rescan setting can turn off even startup rediscovery
- manual rescan is a real part of operational behavior, not just a hidden escape hatch
- watcher exhaustion is recoverable, but only if the operator notices and tunes the runtime

AnonSync should therefore keep one stronger rule:

> detection coverage, observer budget, and fallback latency must be shown as part of steady-state truth, not only in troubleshooting.

## Fixed review order

Every non-trivial detection state or mutation should render the same sections in the same order:

1. **Current detection mode**
2. **Coverage and budget**
3. **Fallback and latency**
4. **Repair and receipt promise**

### 1) Current detection mode

This section should show:

- whether the current mode is `event-driven`, `hybrid`, `periodic-only`, or `manual-only`
- whether the underlying target class is known to degrade notifications
- whether this is a subject-wide posture or only this bind's posture
- whether a recent warning changed the mode automatically

The operator must be able to answer: **how is this share actually learning about changes right now?**

### 2) Coverage and budget

This section should show:

- observed watch coverage
- watcher or observer budget consumption
- any unsupported subtree classes
- whether coverage is complete, partial, exhausted, or unknown
- the specific constraint causing degradation

The operator must be able to answer: **is the runtime actually observing this tree, and where are the blind spots?**

### 3) Fallback and latency

This section should show:

- periodic rescan interval
- whether startup rescans are enabled
- whether manual rescan is available or required
- worst-case discovery delay
- whether current freshness claims are weaker than normal

The operator must be able to answer: **how late could a change be noticed, and why?**

### 4) Repair and receipt promise

This section should show only honest next actions, such as:

- `Healthy real-time coverage`
- `Increase watcher budget`
- `Accept periodic-only coverage`
- `Rebind to a better-supported target`
- `Turn periodic rescan back on`
- `Run one manual rescan now`

The receipt must record the before/after coverage class and latency promise.

## Public objects

### Detection coverage report

Fields:

- `detection_coverage_report_id`
- `subject_ref`
- `bind_ref`
- `detection_mode` (`event-driven`, `hybrid`, `periodic-only`, `manual-only`, `unknown`)
- `target_class` (`local-native`, `network-share`, `overlay-mount`, `deep-tree`, `unknown`)
- `coverage_verdict` (`healthy`, `guarded`, `degraded`, `exhausted`, `unknown`)
- `observer_budget`
- `observer_budget_used`
- `blind_spots[]`
- `generated_at`

### Detection repair review

Fields:

- `detection_repair_review_id`
- `report_ref`
- `requested_action` (`raise-budget`, `change-interval`, `rebind-target`, `manual-rescan`, `accept-degradation`)
- `current_latency_class`
- `post_action_latency_class`
- `risks[]`
- `generated_at`
- `expires_at` nullable

### Detection receipt

Fields:

- `detection_receipt_id`
- `review_ref`
- `applied_action`
- `pre_verdict`
- `post_verdict`
- `pre_latency_class`
- `post_latency_class`
- `completed_at`

## Compact row contract

A truthful compact row should keep these facts in stable order:

1. path or bind
2. detection mode
3. coverage verdict
4. worst-case latency
5. next honest action

Example:

```text
/Volumes/Media     periodic-only     watcher budget exhausted     up to 10m     Increase watcher budget
```

The product should not reduce that to `watching` with a tiny warning badge.

## CLI implications

A minimum public surface should include:

```text
anonsync detect show --path <path>
anonsync detect budget show --bind <bind>
anonsync detect repair plan --bind <bind> --action <action>
anonsync detect repair apply <detection_repair_review_id>
anonsync detect receipt show <detection_receipt_id>
anonsync rescan run --bind <bind>
```

The CLI should let an operator prove whether the system is immediate, periodic, or half-blind without reading support articles.
