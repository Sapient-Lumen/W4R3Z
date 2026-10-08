# Remote-volume path class, notification confidence, and rescan-honesty interface spec

## Purpose

The archive already had change-detection coverage, degraded-target semantics, and execution-seat reachability language.
What it still lacked was one tight contract for a narrower but common operational lie:

> a path that is still reachable enough to sync some bytes, but no longer reachable with the same **change-detection confidence**, **permission posture**, or **settlement freshness**.

Current official Resilio docs make this seam unusually concrete.
They still say a Windows service cannot use mapped drive letters created by interactive logon, that the UNC-style workaround loses system file-update notifications and falls back to learning changes only during rescan or after restart, and that watcher exhaustion on Linux similarly downgrades truth to manual or periodic rescan until the limit is raised.

That is not a mere transport detail.
It is a local-path contract.

## Core decision

AnonSync should classify every bound or candidate path by **path class** and **detection grade**.
A path is not merely `reachable` or `not reachable`.
It must carry at least:

- path class
- permission grade
- detection grade
- freshness cost
- settlement risk

## Path classes

At minimum the product should distinguish:

- `native-local`
- `interactive-mapped`
- `service-visible-remote`
- `namespace-local`
- `external-removable`
- `degraded-visible`
- `unreachable-from-current-seat`

## Detection grades

At minimum the product should distinguish:

- `native-watch`
- `degraded-watch`
- `rescan-periodic`
- `rescan-manual-only`
- `unknown`

The product must never let an operator infer those grades from support folklore.

## Why this matters

Current official Resilio docs still expose four seams AnonSync should not inherit:

- mapped-drive letters can disappear for the service seat even though the human believes the folder `still exists`
- UNC-like fallback can keep bytes flowing while silently dropping immediate change notifications
- watcher exhaustion can degrade freshness without changing the subject into an obvious hard failure
- restart or touch ritual becomes the practical meaning of `sync` if the surface does not publish the downgrade clearly

So AnonSync should keep one harder rule:

> any path admitted under degraded detection must carry that downgrade as a first-class truth on every relevant subject surface.

## Fixed review order

Every path-bind or path-recheck surface should render the same sections in the same order:

1. **Path class now**
2. **Permission and visibility**
3. **Detection confidence**
4. **Freshness and settlement cost**
5. **Allowed intents**
6. **Detection-grade receipt**

### 1) Path class now

This section should show:

- literal path or normalized target label
- current path class
- seat-relative visibility
- whether the class changed because of runtime-seat switch, mount loss, or operator retargeting

The operator must be able to answer: **what kind of storage is this path from the current seat’s point of view?**

### 2) Permission and visibility

This section should show:

- read permission
- write permission
- create/rename/delete confidence
- whether the path is discoverable, manually typable, or fully browsable only from another seat

The operator must be able to answer: **can this seat really operate this target, or only partly reach it?**

### 3) Detection confidence

This section should show:

- detection grade
- watcher substrate or scan substrate
- what events are learned immediately versus only on scan/restart
- any known system budget problem causing the downgrade

The operator must be able to answer: **how does the daemon learn about local changes here?**

### 4) Freshness and settlement cost

This section should show:

- expected freshness window
- whether writer contention or restore flows become less trustworthy under this grade
- whether `ready` can still be asserted strongly
- whether a degraded grade increases risk of surprise archive/revert/recheck behavior

The operator must be able to answer: **what semantic cost comes with keeping this path under the current grade?**

### 5) Allowed intents

This section should show:

- continue with warning
- narrow to inspect-only
- require periodic-rescan posture explicitly
- block for high-fidelity subjects
- move to healthier storage class

The product must not treat all subject kinds equally here.
A degraded path that may be acceptable for loose backup may be unacceptable for tight collaborative work.

### 6) Detection-grade receipt

This section should show:

- path class
- detection grade
- why the grade is what it is
- which intents were allowed or blocked under that grade
- follow-up obligations (raise watchers, move path, switch seat, etc.)

## Public objects

### `bound_path_fact`

Fields:

- `bound_path_fact_id`
- `subject_ref`
- `execution_seat_ref`
- `path_label`
- `path_class`
- `permission_grade`
- `detection_grade`
- `freshness_window_budget`
- `observed_limitations[]`
- `verified_at`

### `path_detection_receipt`

Fields:

- `path_detection_receipt_id`
- `bound_path_fact_ref`
- `review_ref` nullable
- `allowed_intents[]`
- `blocked_intents[]`
- `followup_actions[]`
- `created_at`

## Main surface

A compact status row should read like:

- `native-local · native watch`
- `service-visible remote · periodic rescan only`
- `interactive-mapped · unreachable from current seat`
- `native-local · watch budget exhausted; periodic rescan until fixed`

Not just `available`.

## Event language

Use phrases such as:

- `path detection downgraded from native watch to periodic rescan`
- `mapped path unavailable to current service seat`
- `remote-volume workaround keeps bytes flowing but not immediate local-change notices`
- `watcher budget exhausted; freshness now scan-bound`

Avoid phrases such as:

- `folder okay`
- `share connected`
- `path accessible`

Those are not truthful enough.

## CLI shape

```text
anonsync path inspect <subject>
anonsync path review <subject> --seat <seat>
anonsync path detection receipt <subject>
```

## Edge cases

### Path is writable but not watchable

The product must show that as degraded, not healthy.
Bytes alone are not the whole contract.

### Watchers are exhausted temporarily

A reviewed temporary downgrade is allowed, but the surface must publish the freshness cost and the exit condition.

### Same path class, different intent

A low-priority archival subject may accept a weaker grade than a latency-sensitive shared workspace.
That policy difference should be explicit.

## Non-clone reason

Current official Resilio docs still let meaningful local-path truth hide behind mapped-drive lore, UNC fallback, watcher tuning, and restart/rescan ritual.
AnonSync should instead publish one path-class and detection-grade contract so the operator can tell exactly what kind of local truth they still have before pretending a degraded seat is healthy.
