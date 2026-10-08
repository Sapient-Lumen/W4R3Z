# Upgrade availability, rollout channel, and restart review interface spec

## Purpose

The archive already had release-cohort compatibility and service-world continuity doctrine.
What it still lacked was one operator-facing contract for the everyday question:

> does this seat know that an update exists, is it actually eligible to receive it here, what rollout channel is in effect, and what restart or re-entry cost will apply if I upgrade now?

Current Resilio docs still make this seam concrete.
Desktop preferences still offer update checks on startup and manual check-now, but the update guide still says manual check is not available in WebUI, not all versions are pushed to mass/autoupdate, and failed automatic installation falls back to manual website download and install.

That means `update available` still is not one truthful state across desktop, WebUI, headless, and service worlds.

## Core decision

AnonSync must treat upgrades as reviewed **cohort moves with visible availability state**.
Every seat should be able to answer from its current surface:

- current running version and release cohort
- latest known compatible target for this seat class
- whether the update is visible here, downloadable here, and installable here
- what restart, re-entry, or migration cost applies

## Why this matters

Current Resilio behavior still leaves update truth scattered across:

- desktop startup checks
- a manual `Check now` control
- a separate website/manual installer path
- WebUI lacking the same check surface
- rollout notes that not all builds are pushed to mass/autoupdate

AnonSync should instead hold one stronger rule:

> availability, eligibility, and completion cost belong on one upgrade review.

## Fixed review order

Every upgrade review should render the same sections in the same order:

1. **Current seat posture**
2. **Known target builds**
3. **Availability and rollout channel**
4. **Completion and restart cost**
5. **Upgrade receipt**

### 1) Current seat posture

Show:

- running version
- channel / cohort
- seat class (`desktop`, `local-web`, `headless`, `service`, `mobile`, `other`)
- config/declaration posture if it affects upgrade shape
- current readiness blockers

### 2) Known target builds

Show:

- latest known compatible build for this seat class
- latest known installed cohort among linked or cooperating seats, if relevant
- whether the target is security-critical, recommended, optional, or blocked
- whether a newer build exists but is not yet eligible for this seat/channel

### 3) Availability and rollout channel

Show:

- `visible here` yes/no
- `downloadable here` yes/no
- `installable here` yes/no
- `rollout channel` (`automatic`, `manual`, `staged`, `blocked`, `unknown`)
- source of truth for the availability decision

### 4) Completion and restart cost

Show:

- whether restart is required
- whether re-entry / migration review will follow
- whether local-web/session continuity is preserved or interrupted
- expected proof that the upgrade completed successfully

The operator must be able to answer:

> if I upgrade from this surface now, what will interrupt and what later proves it finished correctly?

### 5) Upgrade receipt

The receipt must preserve:

- version before/after
- rollout channel used
- seat/surface used to initiate
- restart or re-entry steps completed
- compatibility checks passed or deferred

## Main surface

Every seat should expose one **Upgrade** page and one compact summary row such as:

- `New build known, but this local-web seat cannot install it directly.`
- `Update is staged for this cohort; manual fetch is available now.`
- `Upgrade ready; restart required and post-upgrade compatibility review queued.`

## Object model implications

### Upgrade availability report

Fields:

- `upgrade_availability_report_id`
- `seat_ref`
- `running_version`
- `seat_class`
- `current_channel`
- `candidate_targets[]`
- `selected_target`
- `visibility_status`
- `installability_status`
- `rollout_channel`
- `generated_at`

### Upgrade review

Fields:

- `upgrade_review_id`
- `availability_report_ref`
- `selected_target`
- `restart_required`
- `reentry_review_required`
- `compatibility_findings[]`
- `recommended_actions[]`

### Upgrade receipt

Fields:

- `upgrade_receipt_id`
- `review_ref`
- `seat_ref`
- `version_before`
- `version_after`
- `rollout_channel`
- `completed_at`
- `post_upgrade_checks[]`

## Explicit non-goals

AnonSync should not:

- show `up to date` when the surface simply cannot check
- force WebUI/headless operators to discover availability only from a website or release page
- hide restart/re-entry cost behind a generic install button
- blur `newer build exists` together with `this seat can adopt it right now`

## Relationship to nearby specs

This spec is the upgrade-facing companion to:

- `204-release-cohort-compatibility-control-plane-migration-and-link-gate-interface-spec.md`
- `213-service-promotion-migrate-clean-and-principal-continuity-interface-spec.md`
- `221-control-listener-binding-loss-and-safe-exposure-interface-spec.md`
- `208-suspended-seat-resume-quarantine-and-offline-precedence-interface-spec.md`

Those documents already cover compatibility, service-world, and re-entry doctrine.
This one fixes the operator-facing upgrade truth before and after the move.
