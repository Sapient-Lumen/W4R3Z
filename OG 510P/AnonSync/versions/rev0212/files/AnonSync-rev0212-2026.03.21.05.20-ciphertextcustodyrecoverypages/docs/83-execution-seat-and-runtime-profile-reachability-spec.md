# Execution-seat and runtime-profile reachability spec

The archive already has state roots, service profiles, bring-up review, mutation gates, target custody, and channel parity.
This document answers the narrower practical question those abstractions still left open:

> what must a real operator surface literally show when the same host changes runtime principal or service seat, so AnonSync does not drift back into current-user vs service-account folklore, mapped-drive surprises, UNC workaround magic, or `my shares disappeared` archaeology?

This is the execution-seat companion to `42-state-root-and-service-profile-spec.md`, the runtime-world companion to `78-bringup-and-control-entry-interface-spec.md`, and the host-local continuity companion to `82-safety-critical-channel-parity-and-surface-capability-spec.md`.

## Why this needs its own spec

Resilio's docs make the seam unusually clear.
`Running Sync as a service on Windows` says the service can run as current user, `Local System`, or `Local Service`, and that installation can migrate existing state or create a clean service install.
`Sync Service Troubleshooting on Windows` says mapped drive letters are unavailable to the service because services do not receive interactive logon mapping, that the UNC workaround loses immediate file-update notifications and falls back to rescan or restart, and that switching the service to `Local System` opens a different storage folder with no old shares visible until the operator re-adds and re-shares them.
`Sync Storage folder` separately says the storage path differs by service account.
`Guide to Linux, and Sync peculiarities` adds that Linux has no OS integration and needs more manual runtime setup.

The lesson is not merely that services are annoying.
The lesson is that a useful product can still leave one of the most dangerous host-local questions under-specified:

- am I still opening the same durable state, or did a different storage root silently become active?
- can this runtime seat still reach the same targets, or do some paths exist only in the previous seat?
- did a workaround preserve the same local semantics, or did freshness quietly degrade to rescan-only best effort?
- is this really `background the same node`, or is it `start a different local world and reconnect it by hand`?

AnonSync should not clone that shape.

## Core rule

Every runtime/service-seat change should have one server-declared continuity identity and one review identity.
A switch may be:

- same root / same reachable world
- same root / reachable world narrowed
- same root / reviewed rebind required
- clean-seat start
- inspect-only / blocked

A switch may not silently redefine the active state universe, hide path loss behind a successful service start, or claim continuity when freshness guarantees materially degraded.

## Which actions are in scope

This spec is primarily about host-local runtime changes whose meaning cannot be allowed to hide in launch ritual.
That includes at least:

- workstation -> background service
- current-user service -> `Local System` or `Local Service`
- named service user -> another named service user
- maintenance or recovery seat entry that opens or inspects current state
- containerized / namespace-scoped seat changes
- any switch where target reachability, root visibility, or notification posture changes

Low-risk same-seat restart can stay lighter.
High-signal seat changes cannot.

## Vocabulary

### Execution seat

An execution seat is the concrete host-local runtime seat through which the daemon operates.
It combines:

- service profile
- runtime principal / user or service account
- path world and mount namespace
- notification substrate and freshness posture
- control-surface set and mutation capability posture

The point of the seat is not branding.
It is to make the practical host-local world inspectable.

### Seat-switch review

A reviewed case that answers whether changing execution seat preserves the same durable state, the same reachable targets, and the same freshness guarantees.

### Seat-switch receipt

A durable record proving what runtime seat change was actually applied, what continuity was preserved, and what fallout remained.

## Fixed review order

Every non-trivial execution-seat review should render the same sections in the same order:

1. **Requested seat switch and continuity intent**
2. **State root and identity continuity**
3. **Reachable-target delta**
4. **Freshness and substrate delta**
5. **Fallout and admissible actions**
6. **Receipt promise**

### 1) Requested seat switch and continuity intent

This section should show:

- source seat and target seat
- requested intent (`preserve same node`, `background it`, `inspect only`, `clean service start`, `migrate with rebind`)
- whether the action is low-risk restart, guarded switch, or high-signal local-world change
- which review family owns the action (`seat-switch`, `bringup`, `successor`, `other`)

The operator must be able to answer: **what runtime world am I leaving, what one am I trying to enter, and what continuity story am I asking the product to preserve?**

### 2) State root and identity continuity

This section should show:

- whether the same state root remains open, needs explicit attach, or would be replaced
- whether identity continuity remains intact, becomes inspect-only, or would require successor/recovery handling
- whether the target seat widens or narrows mutation capability compared with the source seat
- whether the action is still `same node under a new seat` or really `new node / new root`

The operator must be able to answer: **am I still operating the same durable node, or did the runtime change cross into a different state universe?**

### 3) Reachable-target delta

This section should show:

- which currently known targets remain reachable from the target seat
- which paths become unreachable, remapped, or require reviewed workaround posture
- whether path strings are merely visible versus writable and watchable from the target seat
- whether any existing bind or target-custody assumption must be reopened

The operator must be able to answer: **what local targets, mounts, or path classes change meaning under the new seat?**

### 4) Freshness and substrate delta

This section should show:

- whether notification posture stays native, becomes degraded, or falls to rescan-only
- whether the path-resolution mode changes (`direct-local`, `mapped`, `UNC`, `namespace-scoped`, other)
- whether any workaround weakens settlement, readiness, or writer-contention truth
- whether the requested action still satisfies the original freshness promise

The operator must be able to answer: **did continuity preserve only bytes, or did it also preserve the quality of local truth?**

### 5) Fallout and admissible actions

This section should show:

- whether the honest next step is switch now, prepare rebind, narrow to inspect-only, or open a clean-seat start
- whether target-custody, bring-up, or capacity/fidelity review must reopen
- whether some targets must be deliberately dropped or converted before the switch can remain honest
- what shortcuts are blocked because they would hide state/path/freshness loss

The operator must be able to answer: **what must I do next to keep this runtime change truthful?**

### 6) Receipt promise

This section should show:

- which seat-switch receipt will exist after apply, defer, or refusal
- what it will later prove about source seat, target seat, continuity outcome, reachability delta, freshness delta, and follow-up obligations
- whether the receipt remains provisional because rebind or later verification is still pending
- where later audit survives if the switch is resumed from another channel

The operator must be able to answer: **what later evidence will prove that this runtime change preserved continuity honestly — or that it did not?**

## Public objects

### Execution seat

Fields:

- `execution_seat_id`
- `service_profile_ref`
- `principal_class`
- `principal_label`
- `state_root_ref` nullable
- `reachable_mount_roots[]`
- `path_resolution_mode`
- `notification_posture`
- `control_channel_set[]`
- `mutation_capabilities[]`
- `last_verified_at` nullable
- `provenance_ref` nullable

### Seat-switch review

Fields:

- `execution_seat_review_id`
- `source_execution_seat_ref`
- `target_execution_seat_ref`
- `requested_intent`
- `continuity_expectation`
- `reachability_findings[]`
- `freshness_findings[]`
- `fallout_findings[]`
- `action_options[]`
- `seat_transition_report_ref`
- `generated_at`
- `expires_at` nullable

### Seat-switch receipt

Fields:

- `execution_seat_receipt_id`
- `review_ref`
- `source_execution_seat_ref`
- `target_execution_seat_ref`
- `continuity_summary`
- `reachability_summary`
- `freshness_summary`
- `outcome_summary`
- `actor_ref`
- `created_at`

## What the surface must never imply

The execution-seat surface must never imply that these are the same thing:

- a successful service start versus preserving the same state root
- seeing a familiar path string versus being able to write and watch that target honestly
- a UNC or namespace workaround versus the same native local semantics
- backgrounding the same node versus starting a clean seat that later reconnects manually
- principal change versus ordinary channel handoff
- missing inventory because of seat drift versus explicit reviewed detach or exit

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## Linux/headless parity rule

A Linux-first product has to assume that runtime-seat changes will be entered from SSH, service managers, maintenance shells, browser workbenches, and recovery environments.
So execution-seat truth must survive across those surfaces.
It is not acceptable for one richer surface to show continuity, reachability, and freshness delta while headless control falls back to installer choice, `systemctl` success, or path-lookup troubleshooting.

## Relationship to nearby specs

Execution-seat review should often hand off to nearby review families, but it should not dissolve into them.

- **State-root and service-profile work** explains the durable state and runtime objects.
  Execution-seat review explains whether switching seat preserves the same practical host-local world.
- **Bring-up review** explains whether first open is fresh, attached, recovered, or blocked.
  Execution-seat review explains whether a runtime change is still continuity-preserving or really a new-world bring-up.
- **Target-custody review** explains who already owns one path.
  Execution-seat review explains whether that path remains reachable or honest under the new seat.
- **Channel-parity review** explains how one reviewed action survives client changes.
  Execution-seat review explains how the host-local world itself changes under the daemon.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync state seat show <execution_seat_review_id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether the new seat preserves the same state, loses targets, degrades freshness, or really becomes a clean runtime world.

## Why this is worth the trouble

AnonSync only justifies its extra interface complexity if runtime changes also become easier to trust.
A fixed execution-seat grammar is how the archive avoids rebuilding a system where service-account choices, mapped-drive disappearance, UNC fallback, changed storage roots, and re-add/re-share instructions are all individually documented, yet the full meaning of `is this still the same node, and what host-local truth changed when I switched runtime seat?` still depends on which support article the operator happened to remember first.
