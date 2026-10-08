# Locked-writer delay profile and quiescent commit interface spec

## Purpose

The archive already had commit barriers, convergence honesty, and detection-coverage truth.
What it still lacked was one interface contract for a very common edge:

> when a document editor, CAD tool, or other writer keeps a file half-finished or locked, what page proves whether the product is waiting intentionally, retrying blindly, or about to publish a not-yet-quiescent result?

Current official Resilio docs make this seam more concrete than a generic `locked files happen` shrug would.
They still say locked files are visible only as a list of blocked paths, that Sync cannot identify which application owns the lock, and that editor-friendly delay behavior is configured through a `FileDelayConfig` JSON in the storage folder and takes effect only after restart.
Power-user preferences still expose a separate locked-file recheck interval.

That is useful escape-hatch flexibility.
It is still not a good public commit contract.

## Core decision

AnonSync should make **writer quiescence** first-class and attach it to publication truth.

Every subject containing files under active edit pressure must always declare:

- which paths are lock-blocked versus merely delayed
- the active delay profile
- whether a publish candidate is quiescent, provisional, or blocked
- what evidence says a writer has actually finished
- what retry cadence is active
- what operator action would safely advance the file

If an operator still has to infer `we are intentionally waiting for the editor` from a support article, a hidden JSON, or repeated retries, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal six truths AnonSync should not clone:

- `file changed` does not imply `safe to publish now`
- lock-blocked and delay-buffered are different states with different remedies
- application-specific commit timing is a public behavior, not a private tweak
- restart-gated delay profile changes weaken operational confidence
- a sync engine may know a path is blocked without knowing why, so uncertainty itself must be visible
- quiescence policy hidden in storage/config files turns content-safety into folklore

AnonSync should therefore keep one stronger rule:

> files under active writer pressure must publish quiescence truth, delay policy, and retry posture as ordinary state, not as hidden tuning.

## Fixed review order

Every lock- or delay-related review should render the same sections in the same order:

1. **Writer pressure now**
2. **Delay and retry policy**
3. **Quiescent commit evidence**
4. **Repair and publication receipt**

### 1) Writer pressure now

This section should show:

- whether a file is `quiescent`, `delay-buffered`, `lock-blocked`, or `uncertain`
- which path or paths are affected
- whether the state came from an observed lock, safe-save pattern, or manual hold
- whether publication is currently allowed, held, or review-required

The operator must be able to answer: **is this file ready to leave the machine?**

### 2) Delay and retry policy

This section should show:

- active delay profile name
- delay duration and scope
- locked-file retry interval
- whether the policy is inherited, edited locally, or temporary
- whether any pending change requires restart or hot-reload

The operator must be able to answer: **what is the runtime waiting for, and for how long?**

### 3) Quiescent commit evidence

This section should show:

- last stable size/mtime/hash observation
- whether a lock has cleared
- whether the candidate content remained unchanged for the minimum quiet window
- whether downstream publication would still be provisional

The operator must be able to answer: **what evidence proves that the writer is done enough?**

### 4) Repair and publication receipt

This section should show only honest next actions, such as:

- `Wait for quiet window`
- `Retry after lock clears`
- `Hold publication until manual review`
- `Apply stronger delay profile`
- `Mark tool as safe for immediate commit`

The receipt must record which files were held, when they became quiescent, and whether publication resumed automatically or by review.

## Public objects

### Writer pressure report

Fields:

- `writer_pressure_report_id`
- `subject_ref`
- `paths[]`
- `state` (`quiescent`, `delay-buffered`, `lock-blocked`, `uncertain`)
- `observed_lock` boolean
- `delay_profile_ref` nullable
- `retry_interval_seconds` nullable
- `generated_at`

### Quiescence review

Fields:

- `quiescence_review_id`
- `report_ref`
- `requested_action` (`wait`, `publish-anyway`, `change-delay-profile`, `hold-for-review`, `manual-retry`)
- `quiet_window_seconds`
- `publication_effect`
- `risks[]`
- `generated_at`
- `expires_at` nullable

### Quiescence receipt

Fields:

- `quiescence_receipt_id`
- `review_ref`
- `files_released[]`
- `files_held[]`
- `pre_state`
- `post_state`
- `completed_at`

## Compact row contract

A truthful compact row should keep these facts in stable order:

1. path
2. writer-pressure state
3. delay profile or lock evidence
4. publication posture
5. next honest action

Example:

```text
/report.xlsx     delay-buffered     office-safe 45s     hold publish     Wait for quiet window
```

The product should not reduce that to `syncing soon` or `locked` without showing what that means for content safety.

## CLI implications

A minimum public surface should include:

```text
anonsync writer show --path <path>
anonsync writer delay profiles
anonsync writer plan --path <path> --action <action>
anonsync writer apply <quiescence_review_id>
anonsync writer receipt show <quiescence_receipt_id>
```

The CLI should let an operator prove whether a file is safely quiescent before a propagation or snapshot action relies on it.
