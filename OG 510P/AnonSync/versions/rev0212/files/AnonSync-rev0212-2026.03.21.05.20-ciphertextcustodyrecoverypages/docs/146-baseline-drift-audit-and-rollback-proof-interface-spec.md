# Baseline drift audit and rollback proof interface spec

## Purpose

Once standing mutations become explicit **baseline rollout drafts**, another seam appears immediately:

- after rollout, how do we know which targets actually inherited the intended baseline?
- which differences are sanctioned exceptions versus accidental drift?
- when should the system repair drift, preserve it, or roll the baseline back?
- how does rollback itself prove that the old state was actually restored?

This document defines the interface contract for **baseline drift audit**, **exception-aware divergence classification**, and **rollback proof**.

## Core rule

Every approved standing rollout must eventually produce a fresh **drift audit**.
The product must not assume that because a baseline was approved, every named target now matches it.

It must distinguish at least four states:

1. `matches baseline`
2. `matches with explicit exception`
3. `diverged without exception`
4. `not yet observed well enough to classify`

## Why this needs its own spec

Current official Resilio docs again sharpen the need for this boundary.

They currently describe a world where meaning can spread through linked-device defaults, share defaults, host preferences, configuration files, and copied parameters across machines.
They also describe cases where config-mode folders override previously added WebUI folders, where launch mode matters, and where later reconnect/adoption behavior can yield duplicate paths or changed effective location.

That means a standing rollout can be *intended* centrally or manually and still leave operators asking afterward:

- which machines really launched with the new config?
- which shares kept a manual override and therefore no longer inherit the default?
- which members remain on an older arrival posture?
- which divergences are legitimate local exceptions?
- what exactly would rollback touch?

AnonSync should answer those questions directly instead of letting them hide in later behavior.

## Public objects

### Baseline drift audit

The durable object summarizing one post-rollout observation pass.

Suggested fields:

- `baseline_drift_audit_id`
- `baseline_rollout_ref`
- `audit_scope_summary`
- `observed_at`
- `audit_state` (`draft`, `partial`, `fresh`, `stale`, `superseded`)
- `match_count`
- `exception_match_count`
- `drift_count`
- `unobserved_count`
- `rollback_recommendation_state` (`none`, `targeted-repair`, `partial-rollback`, `full-rollback`, `manual-review-required`)

### Target effective-state row

One observed target and its effective relationship to baseline.

Suggested fields:

- `target_effective_state_row_id`
- `target_ref`
- `effective_state_summary`
- `classification` (`matches`, `matches-with-exception`, `drifted`, `unobserved`, `inconclusive`)
- `strongest_reason`
- `evidence_ref`
- `last_fresh_observation_at`

### Exception lineage row

One sanctioned reason a target differs from the nominal baseline.

Suggested fields:

- `exception_lineage_row_id`
- `target_ref`
- `exception_object_ref`
- `exception_kind` (`subject-level`, `member-level`, `host-level`, `incident-overlay`, `platform-exclusion`, `manual-preservation`)
- `still-valid` bool
- `future_effect_if_preserved`

### Drift repair row

One suggested repair or reclassification action.

Suggested fields:

- `drift_repair_row_id`
- `target_ref`
- `repair_kind` (`reobserve`, `adopt-baseline`, `record-exception`, `targeted-rollback`, `full-rollback-candidate`)
- `why_suggested`
- `collateral_summary`
- `proof_required_after_run`

### Rollback proof object

The durable summary shown after a rollback or targeted repair completes.

Suggested fields:

- `rollback_proof_id`
- `rollback_ref`
- `rollback_scope_summary`
- `restoration_verdict` (`proved-restored`, `partially-restored`, `residual-drift`, `could-not-prove-restored`)
- `remaining_drift_summary`
- `followup_ref` nullable

## Fixed inspection order

Every drift-audit surface should preserve this order:

1. **What baseline was supposed to hold**
2. **What was actually observed per target**
3. **Which differences are sanctioned exceptions**
4. **Which differences are unsanctioned drift**
5. **What rollback or repair would touch**
6. **Accept exception, repair target, roll back baseline, or keep observing**

### 1) What baseline was supposed to hold

The surface should restate the rollout intent.
Examples:

- `members in cohort C should default to arrival root R`
- `hosts in cohort H should use TTL 5 for new single-file offers`
- `future unchanged shares under template T should inherit priority P`

### 2) What was actually observed per target

This section must be target-specific.
Examples:

- `host A matches baseline`
- `member B still shows older future-arrival root`
- `host C unobserved since rollout`
- `share S no longer inherits baseline because manual override exists`

### 3) Which differences are sanctioned exceptions

The product should lift exceptions out of the drift bucket.
Examples:

- `member D excluded by platform exception`
- `share S intentionally pinned to local priority None`
- `host H still under incident overlay lease`

### 4) Which differences are unsanctioned drift

Drift should be explicit and evidence-backed.
Examples:

- `target was in rollout cohort but latest observed effective state differs`
- `no exception object explains divergence`
- `rollback of old default is incomplete`

### 5) What rollback or repair would touch

The operator should see the smallest honest repair boundary.
Examples:

- `repair only member B and host C`
- `record exception for mobile cohort`
- `roll back baseline for all workstation hosts`

### 6) Accept exception, repair target, roll back baseline, or keep observing

The call to action should match the strongest evidence:

- `Accept as explicit exception`
- `Repair target drift`
- `Rollback standing baseline`
- `Keep observing; not enough fresh evidence yet`

## Public rules

### Rule 1 — drift is not the same as unobserved

A target with stale or missing evidence must not be mislabeled as drift merely because it was in the cohort.

### Rule 2 — exception lineage must be visible

Any sanctioned deviation must point to the object that authorizes it.
Otherwise it is just unexplained drift.

### Rule 3 — rollback must preview its scope

Before rollback runs, the product must show whether it touches all targets, only drifted targets, or only future inheritance.

### Rule 4 — rollback needs proof too

A rollback is still a mutation.
It must end with fresh observation and a restoration verdict.

### Rule 5 — preserved manual overrides must be explicit

If a target stopped inheriting a baseline because of a manual override, that fact must be surfaced directly, not inferred from outcome alone.

### Rule 6 — a standing rollout is incomplete without post-rollout audit

Approval alone is not enough.
Standing changes remain under-specified until the product can show who actually matches them.

## Dense row contract

A dense drift-audit row should preserve these labels in this order:

- `Target`
- `Expected baseline`
- `Observed effective state`
- `Exception lineage`
- `Drift verdict`
- `Repair/rollback option`
- `State`

## Example prompts

- `Which targets actually inherited this baseline?`
- `Is this difference a sanctioned exception or accidental drift?`
- `What would rollback touch right now?`
- `Which targets are merely unobserved, not divergent?`
- `Did rollback really restore the older baseline?`

## Anti-goals

- do not treat missing evidence as proof of compliance
- do not treat any difference as drift when a valid exception exists
- do not let rollback hide inside generic history without restoration proof
- do not force the operator to reconstruct effective baseline from copied config or later outcome
