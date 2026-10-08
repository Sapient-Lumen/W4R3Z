# Space pressure, reclaim, and retention budget spec

## Problem this spec resolves

The archive already had several neighboring ideas:

- selective materialization and placeholder-visible mounts
- preservation reports for destructive actions
- history/rollback retention and restore surfaces
- filesystem-fidelity contracts for pathname, metadata, and notification truth
- settlement and activity surfaces that can already explain when background work is still active

What it still lacked was one dedicated answer to the operator question:

> where is local space going, which classes of bytes can I reclaim safely, what retention rules are consuming space on purpose, what pressure policy is active, and what receipt proves I reclaimed or preserved the right thing?

Another current Resilio pass makes that gap concrete.
Their official docs still spread storage truth across separate support surfaces:

- Selective Sync and mobile Selective Sync are sold as space-saving modes built around placeholders and on-demand bytes
- linked-device UI can show a device storage status, but storage is still described as a device or mode attribute more than a durable public ledger
- Archive retention lives in hidden `.sync/Archive`, keeps data for 30 days on desktop and 1 day on mobile by default, supports manual restore only, and can be set never to clean up if `sync_trash_ttl=0`
- power-user preferences describe `free_space_warning_threashold`, `log_size`, `log_ttl`, and `max_file_size_for_versioning`, while the troubleshooting page separately says syncing can stop when the downloading device runs out of free space
- the same troubleshooting page tells operators to inspect hidden `.!sync` partial-download remnants by hand
- the storage-folder page and uninstall guide separately explain that databases, logs, profiler output, and hidden Archive/service data live in different paths and may continue consuming space after uninstall unless manually removed
- iOS has a storage screen that breaks usage into app data and user data, but that shape is not the general product contract

Those are not trivial documentation quirks.
They are evidence that space pressure, reclaim scope, and retention budget are still not one public operator model.

AnonSync should not clone that shape.

## Core rule

Space pressure is a **first-class budget contract**, not an after-the-fact troubleshooting state.

That means:

1. mounts and devices should publish a space ledger, not just rough free-space warnings
2. reclaim should be explicit about byte class and blast radius, not inferred from file gestures or hidden caches
3. retention should have public policies and explainable storage cost, not hidden TTL folklore
4. low-space behavior should be policy-bearing and receipt-bearing
5. pressure should integrate with readiness, activity, and preservation rather than living in a separate panic-only UI path

If the operator still has to combine placeholder intuition, hidden Archive growth, power-user thresholds, storage-folder lore, and manual `.!sync` cleanup steps to answer “what is consuming space here and what can I safely reclaim?”, the public model is not explicit enough.

## Vocabulary

### Space ledger

A durable accounting view that groups local disk use by byte class rather than by implementation accident.

### Budget policy

A durable policy that defines soft and hard pressure thresholds, reclaim preferences, and whether specific retention classes may auto-trim or only warn.

### Pressure case

A public warning object describing that a device, state root, or mount is nearing or exceeding a budget boundary.

### Reclaim plan

A preview object describing which byte classes would be evicted, trimmed, compacted, or preserved by a proposed reclaim action.

### Reclaim receipt

A durable record proving what storage-affecting action was taken, which bytes moved or disappeared, and what preservation/retention implications were accepted.

## Non-negotiable design rules

1. **No hidden-byte class contract.**  
   Implementation files may exist, but operators should not need to know hidden cache, temp, or archive paths to understand where local space went.

2. **Pressure must be explainable by class.**  
   “Low disk space” is not enough. The product must separate materialized bytes, placeholder-visible state, archive/history bytes, daemon/state bytes, logs, transient download remnants, and preserved local deviations.

3. **Reclaim scope must be explicit.**  
   A reclaim action must say whether it affects local materialized bytes only, queue/temp bytes only, retention history, or replicated share state.

4. **Retention and reclaim must stay separate.**  
   Lowering history retention, evicting local materialized bytes, compacting logs, and deleting replicated share files are different actions even if all free space.

5. **Pressure policy must be public.**  
   Warning threshold, hard-stop threshold, and allowed automatic trims should be visible and inspectable.

6. **Receipts should prove what was freed and what was preserved.**  
   Later audit should be able to answer not merely that “space was reclaimed,” but which classes changed and whether rollback/history posture weakened.

## Object-model additions

### Budget policy

Fields:

- `budget_policy_id`
- `name`
- `scope` (`system`, `state-root`, `share-default`, `mount-default`, `mount-specific`)
- `soft_pressure_threshold_bytes`
- `hard_pressure_threshold_bytes`
- `warning_floor_bytes` nullable
- `auto_trim_classes[]` (`logs`, `temp-downloads`, `stale-plans`, `old-profiler`, `none`)
- `history_trim_policy` (`warn-only`, `review-required`, `auto-trim-reviewed`, `disabled`)
- `materialization_preference` (`keep-hot`, `evict-cold-first`, `manual-only`)
- `queue_temp_cleanup_policy` (`auto-compact`, `warn-manual`, `review-required`)
- `created_at`
- `provenance_ref` nullable

### Space ledger

Fields:

- `space_ledger_id`
- `subject_ref`
- `subject_kind` (`system`, `state-root`, `share`, `mount`, `device`)
- `total_bytes`
- `free_bytes`
- `tracked_classes[]`
- `class_totals` object containing at least:
  - `materialized_bytes`
  - `placeholder_namespace_bytes`
  - `archive_history_bytes`
  - `local_deviation_preserve_bytes`
  - `temp_download_bytes`
  - `state_db_bytes`
  - `log_bytes`
  - `transport_runtime_bytes`
  - `other_service_bytes`
- `pressure_state` (`healthy`, `watch`, `guarded`, `high`, `blocked`)
- `budget_policy_ref` nullable
- `last_sampled_at`
- `provenance_ref` nullable

### Pressure case

Fields:

- `pressure_case_id`
- `space_ledger_ref`
- `budget_policy_ref`
- `trigger_kind` (`soft-threshold`, `hard-threshold`, `runway-shortfall`, `unexpected-growth`, `temp-remnant-buildup`, `history-over-budget`)
- `dominant_classes[]`
- `estimated_runway_bytes` nullable
- `estimated_runway_time` nullable
- `recommended_actions[]`
- `generated_at`
- `severity` (`watch`, `guarded`, `high`, `blocked`)
- `provenance_ref` nullable

### Reclaim plan

Fields:

- `reclaim_plan_id`
- `subject_ref`
- `scope` (`system`, `state-root`, `share`, `mount`, `selection`)
- `candidate_actions[]`
- `freed_bytes_estimate`
- `preserved_bytes_estimate`
- `class_effects[]`
- `history_effect` (`none`, `trim`, `review-required`, `blocked`)
- `replicated_state_effect` (`none`, `blocked`)
- `generated_at`
- `provenance_ref` nullable

### Reclaim receipt

Fields:

- `reclaim_receipt_id`
- `subject_ref`
- `reclaim_plan_ref` nullable
- `action_kind` (`evict-materialized`, `trim-history`, `compact-temp`, `compact-logs`, `accept-pressure-policy`, `cancelled-noop`)
- `freed_bytes_actual`
- `classes_changed[]`
- `history_effect`
- `preservation_report_ref` nullable
- `completed_at`
- `provenance_ref` nullable

## Minimum byte classes the product should expose

Even if implementation uses more internal buckets, the public model should expose at least these classes:

- **Materialized bytes** — local full-content copies currently resident for one or more mounts
- **Placeholder-visible bytes** — tiny local namespace artifacts that do not represent full local content
- **Archive/history bytes** — rollback/version material retained intentionally
- **Deviation-preserve bytes** — quarantined or preserved local edits retained for review
- **Temporary download bytes** — partial or staged transfer content not yet settled
- **State/DB bytes** — metadata, indexes, decision traces, and daemon state
- **Logs/profiler bytes** — observability artifacts with trim-friendly posture
- **Transport/runtime bytes** — bundled network runtime state where applicable

The operator does not need exact filesystem internals for each bucket, but they do need a stable storage truth.

## Report implications

The common report language should gain a dedicated **space-pressure report** family.

It should answer at least:

- which subject is under pressure
- which classes dominate usage or growth
- whether the current state is warning-only, guarded, or blocking new materialization
- what reclaim actions are available without affecting replicated share state
- what retention or preservation posture would weaken if a larger reclaim is chosen

Pressure reports should be renderable from the same report shelf as convergence, preservation, and portability findings.

## CLI implications

A minimum public surface should include:

```text
anonsync space show
anonsync space show --mount <mount>
anonsync space classes --share <share>
anonsync space policy list
anonsync space policy show <policy>
anonsync space pressure list
anonsync space pressure show <pressure_case_id>
anonsync space reclaim prepare --mount <mount> --target-bytes 20GiB
anonsync space reclaim prepare --state-root <srt> --class logs,temp-downloads
anonsync space reclaim apply <reclaim_plan_id>
anonsync space receipt list --subject <mount>
anonsync space receipt show <reclaim_receipt_id>
```

Semantics:

- `space show` answers where space is going right now by byte class
- `space classes` narrows that answer to the requested subject and class breakdown
- `space pressure show` explains why the pressure case fired and what safe-first reclaim options exist
- `space reclaim prepare` must preview freed bytes, preserved bytes, class effects, and retention consequences before apply
- `space reclaim apply` must never widen into replicated delete semantics; share-state mutation should be a different verb entirely
- `space receipt show` should prove what was actually reclaimed and what history/preservation posture changed

## Daemon API implications

A minimum public surface should include:

```text
GET  /v1/space/ledgers
GET  /v1/space/ledgers/{space_ledger_id}
GET  /v1/space/policies
POST /v1/space/policies
GET  /v1/space/policies/{budget_policy_id}
GET  /v1/space/pressure-cases
GET  /v1/space/pressure-cases/{pressure_case_id}
POST /v1/space/reclaim-plans
GET  /v1/space/reclaim-plans/{reclaim_plan_id}
POST /v1/space/reclaim-plans/{reclaim_plan_id}:apply
GET  /v1/space/receipts
GET  /v1/space/receipts/{reclaim_receipt_id}
```

The API should make it possible for CLI, TUI, workbench, and automation to answer storage questions without scraping status lines or inspecting implementation paths on disk.

## Workbench implications

The share detail page should expose one combined **Space & retention** card.

It should answer:

- how much local space this share/mount is consuming by class
- whether pressure is healthy, watch, guarded, high, or blocked
- which budget policy is active
- whether history/archive retention is the dominant storage cost
- whether temp or remnant bytes are abnormal and reclaimable
- what safe-first reclaim action exists
- which reclaim receipt last changed this subject

The system page should also expose one global pressure lane so low-space truth is not trapped inside a single mount page.

## Canonical operator questions this spec should make easy

- “Why is this device low on space — materialized bytes, history retention, temp remnants, or daemon state?”
- “Can I free 20 GiB locally without changing replicated share state?”
- “If I trim history here, what rollback capability do I lose?”
- “Did last night’s reclaim only evict local bytes, or did it weaken retention too?”
- “Which warning threshold or hard-stop policy is blocking new materialization on this mount?”

## Why this is a real non-clone requirement

Resilio already exposes useful ingredients: placeholders, Archive retention, power-user thresholds, and some device-level storage hints. The problem is that the operator still has to reconstruct storage truth from several unrelated surfaces: selective-sync mode explanations, hidden `.sync/Archive`, storage-folder lore, uninstall cleanup notes, iOS-only storage management, and troubleshooting steps for disk-full or stuck temp remnants.

AnonSync should instead expose one honest public model where local space classes, pressure policy, reclaim scope, and retention tradeoffs all render through the same interface grammar.
