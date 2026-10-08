# Storage budget, staging headroom, and actual-drive truth interface spec

## Purpose

The archive already had staged-transfer, placeholder-horizon, service-root, and progress-ledger language.
What it still lacked was one explicit contract for another ordinary but misleading operator moment:

> when the system says there is not enough space, which drive is actually pressured, which subjects are blocked, what hidden reservations still count, and what action buys real headroom instead of only moving the warning somewhere else?

Current official Resilio docs make this seam sharper than a generic red storage badge would.
They still say the core warning for free space is keyed to the disk where the **default folder location** points, and power-user preferences still describe `free_space_warning_threashold` as the amount of remaining space on the drive with the **default folder location** at which Sync warns and stops syncing files.
At the same time Sync Preferences still describe the default folder path as the place where folders created through linked-device arrival in `Selective Sync` or `Synced` mode will be created, plus the default destination for single-file arrival.
The change log also still records several false-positive no-free-space fixes and an option to skip the disk free-space check in older branches.

That is operationally real.
It is still not a good public storage-pressure contract.

## Core decision

AnonSync should make **storage pressure** first-class and **drive-scoped**.

Every storage warning or storage-blocking state must declare:

- which concrete filesystem or mount is pressured
- which subject is consuming or reserving space there
- whether the pressure is due to durable bytes, staging reservation, archive/history retention, or state-root overhead
- whether the risk is on the active subject path, the default arrival root, the service/state root, or a scratch/staging root
- which mitigations actually free usable headroom for the blocked work

If an operator still has to infer from one generic warning whether the problem is a share path, an arrival default, or a hidden state/staging root, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal eight truths AnonSync should not clone:

- storage pressure is still publicly described through the **default folder location** rather than one subject-by-subject pressure ledger
- a warning can therefore point at a policy root that is not obviously the same thing as the currently blocked subject path
- the threshold itself can be changed in power-user preferences, which means storage semantics can move without one visible explanation surface
- past false-positive fixes in the change log show that the warning itself can be noisy enough to deserve stronger proof
- `folder_rescan_interval`, profiler data, debug logs, and other storage-folder residents mean hidden service roots also consume space and disk wakeups
- staged transfer already has its own partial-artifact semantics, so storage truth needs to distinguish *durable bytes* from *temporary reservation*
- archive/history retention can keep old bytes around even when the current subject looks small
- a storage pressure warning that does not name the pressured drive or reserve class invites exactly the wrong action

AnonSync should therefore keep one stronger rule:

> every storage-pressure state must publish a concrete pressure map: drive, root, reserve class, affected subjects, hard floor, and the cheapest honest mitigation.

## Fixed review order

Every non-trivial storage warning should render the same sections in the same order:

1. **Pressure map now**
2. **Reservation and headroom breakdown**
3. **Mitigation ladder**
4. **Receipt and replay promise**

### 1) Pressure map now

This section should show:

- pressured filesystem/mount identifier
- path roots on that filesystem:
  - subject bind root
  - arrival-default root
  - state/service root
  - archive/history root if distinct
  - staging/scratch root if distinct
- current free space
- configured safety floor
- currently blocked actions

The operator must be able to answer: **which real drive is under pressure, and what work is blocked because of it?**

### 2) Reservation and headroom breakdown

This section should show:

- durable materialized bytes
- placeholders only
- current staged partial bytes
- reserved-but-not-yet-written staging budget
- archive/history bytes
- state-root bytes
- estimated bytes needed for the next blocked action
- confidence level for the estimate

The operator must be able to answer: **what is real consumption, what is temporary reservation, and what additional headroom is actually needed?**

### 3) Mitigation ladder

This section should show ordered mitigations such as:

- free bytes on the pressured filesystem
- move the subject bind to another filesystem
- change arrival-default root for future arrivals
- move the state/staging root
- trim archive/history according to policy
- evict local materialization while preserving namespace
- delay or cancel queued large arrivals
- lower non-essential storage retention classes

Each candidate must declare:

- estimated space returned
- whether current blocked work can resume afterwards
- whether continuity changes for any subject
- whether the change is reversible
- whether the mitigation only helps *future* arrivals rather than the *currently blocked* one

The operator must be able to answer: **which action actually fixes this pressure, and which actions merely relocate future work?**

### 4) Receipt and replay promise

This section should show:

- chosen mitigation
- before/after pressure map
- space returned or newly reserved
- any changed policy roots
- durable receipt for future audit and rollback planning

The operator must be able to answer: **what storage action was actually taken, and did it restore enough headroom for the blocked work?**

## Main surface

The subject workspace should expose a **Storage pressure** card whenever a subject is blocked or degraded by capacity.
The card should never say only `low disk space`.
It should say something like:

- `subject bytes fit, but staging root /var/lib/anonsync does not`
- `arrival-default root is full; already bound subjects are healthy`
- `archive retention consumes more than active data on this filesystem`
- `future arrival is blocked; current materialized bytes remain healthy`

The card should link to a reviewed page, not to a raw preference.

## Cross-subject pressure page

The shell should also expose a **Storage map** page that groups pressure by filesystem, not by share.
Each filesystem row should show:

- mount/root
- free bytes
- hard floor
- soft floor
- state bytes
- archive bytes
- staging reservation
- subjects currently blocked there

This is where operators answer: **is the problem one oversized subject, a hot staging root, or the fact that several healthy subjects share one pressured filesystem?**

## Object model implications

AnonSync should add or strengthen these objects:

- `storage_root_record`
- `storage_pressure_case`
- `reserve_class_breakdown`
- `headroom_estimate`
- `storage_mitigation_review`
- `storage_mitigation_receipt`

Suggested fields for `storage_pressure_case`:

- `filesystem_id`
- `root_class` (`subject-bind`, `arrival-default`, `state-root`, `archive-root`, `staging-root`)
- `subject_ids[]`
- `free_bytes_now`
- `safety_floor_bytes`
- `reserved_bytes_by_class`
- `blocked_action_classes[]`
- `estimate_confidence`
- `recommended_next_actions[]`

## Event language

Event stream language should use explicit phrases:

- `storage floor approached`
- `subject blocked by staging-root pressure`
- `arrival-default full; future arrivals paused`
- `archive retention exceeds configured budget`
- `mitigation changed state root`
- `eviction restored headroom without shared deletion`

Avoid vague lines like:

- `disk is almost full`
- `sync stopped because no space`
- `capacity issue detected`

## CLI shape

Example diagnostics:

```text
anonsync subject explain-storage <subject>
anonsync storage map
anonsync storage review --subject <id> --mitigation move-bind --to /srv/data
anonsync storage review --filesystem <id> --mitigation trim-archive
```

The CLI must show the same reserve classes and the same “future-only vs fixes-current-blockage” distinction as the local web UI.

## Failure and edge cases

### Subject path healthy, state root unhealthy

If active bytes live on a roomy disk but staging/state lives on a small system disk, the subject page must say so explicitly.
The fix may be `move state root`, not `move subject`.

### Arrival-default root full, already-bound subjects healthy

A user who only sees a global warning may otherwise fear all current subjects are broken.
The interface must instead say: **future arrivals blocked; current bindings unaffected**.

### Archive-heavy pressure

If history/archive dominates usage, the review must distinguish:
- bytes reclaimable by retention trim
- bytes needed for recovery promises
- bytes that would be lost if trimmed now

### False-positive or stale pressure

If pressure telemetry or path mapping looks inconsistent, the case should degrade to `pressure evidence inconsistent` and block destructive cleanup until a fresh sample is taken.

## The non-clone reason

This is a clean example of why AnonSync should not merely copy Resilio's surface.
Current Resilio docs still leave too much room for an operator to confuse **default arrival root pressure**, **subject-path pressure**, and **hidden service-root pressure**.
AnonSync should instead publish one filesystem-scoped storage ledger where thresholds, reserves, blocked actions, and mitigations are visible in one place.
