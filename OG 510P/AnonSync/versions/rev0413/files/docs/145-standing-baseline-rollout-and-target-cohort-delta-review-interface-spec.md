# Standing baseline rollout and target-cohort delta review interface spec

## Purpose

`rev0119` made the archive explicit about two things that are easy to blur in real systems:

- whether a proposed change is truly an **incident overlay** or a **standing mutation**
- whether a temporary change actually expired cleanly or left **residue** behind

That resolves one dangerous seam.
It immediately exposes the next one:

- if a change really is standing scope, **who exactly inherits it?**
- which current subjects, members, hosts, templates, or future objects will it touch?
- what is the actual rollout cohort?
- what is explicitly excluded?
- what future behavior will differ after rollout?

This document defines the interface contract for turning standing mutations into reviewed **baseline rollout drafts** instead of letting them ride on copied config, global defaults, or operator memory.

## Core rule

Any approved **standing mutation** whose effect reaches beyond one already-named local object must be compiled into a reviewed **baseline rollout draft** before activation.

The product must not let standing behavior spread through:

- copied configuration
- host-level defaults
- template inheritance
- future-share defaults
- member-wide arrival defaults
- `all linked devices` assumptions

without one surface that makes the target cohort and expected deltas explicit.

## Why this needs its own spec

Current official Resilio docs sharpen this need in a useful way.

They currently document:

- linked-device behavior where newly added folders become available across linked devices
- synchronization modes that govern how newly added folders arrive on one linked member
- a default folder location used for linked-device arrivals in `Selective Sync` or `Synced`
- power-user defaults that affect host-level behavior
- `folder_defaults.transfer_priority`, which can affect both existing unchanged shares and future shares
- `share_file_ttl`, which changes the default validity window for single-file shares
- configuration mode explicitly described as a way to apply pre-configured parameters on a number of different machines
- configuration-mode behavior where shared directories specified in configuration override folders previously added from WebUI and disable WebUI for that setup

None of those capabilities are fake.
Several are genuinely powerful.
The problem is that the operator can still encounter them as `just change the default`, `just use this config`, or `just make the template consistent` without one exact rollout object.

AnonSync should instead insist that any real standing mutation answer these questions before apply:

- what baseline is changing?
- who is in the rollout cohort?
- which existing objects are touched?
- which future objects inherit it?
- which members or hosts are explicitly excluded?
- what rollback boundary exists if the rollout turns out too wide?

## Public objects

### Baseline rollout draft

The durable object for one standing change proposed for one explicit cohort.

Suggested fields:

- `baseline_rollout_draft_id`
- `standing_mutation_ref`
- `baseline_kind` (`member-arrival-default`, `share-default`, `host-default`, `fleet-template`, `publication-template`, `issuance-default`, `transport-default`)
- `intent_summary`
- `draft_state` (`draft`, `reviewed`, `approved`, `rejected`, `split-required`)
- `target_cohort_summary`
- `touches_existing_objects` bool
- `touches_future_objects` bool
- `rollback_boundary_summary`

### Target cohort row

One explicit slice of who or what is meant to inherit the standing change.

Suggested fields:

- `target_cohort_row_id`
- `target_kind` (`member`, `member-class`, `host`, `host-class`, `template`, `subject-class`, `future-shares`, `future-offers`)
- `selector_summary`
- `current_count_estimate`
- `future_inheritance_rule`
- `exclusion_count`
- `state`

### Rollout delta row

One concrete behavior difference expected after rollout.

Suggested fields:

- `rollout_delta_row_id`
- `delta_kind` (`path-default`, `materialization-default`, `role-default`, `transport-default`, `priority-default`, `ttl-default`, `issuance-default`, `publication-default`)
- `current_behavior_summary`
- `proposed_behavior_summary`
- `touches_existing_objects` bool
- `touches_future_objects` bool
- `representative_examples`

### Explicit exclusion row

One thing intentionally *not* included in the rollout.

Suggested fields:

- `explicit_exclusion_row_id`
- `excluded_scope_kind`
- `excluded_scope_summary`
- `why_excluded`
- `what_would_need_to_happen_to_include_it`

### Rollout boundary row

One boundary that constrains how far the standing change is allowed to spread.

Suggested fields:

- `rollout_boundary_row_id`
- `boundary_kind` (`named-cohort-only`, `template-bound`, `future-only`, `existing-and-future`, `manual-adoption-required`, `exception-preserving`)
- `boundary_summary`
- `breach_consequence`

## Fixed inspection order

Every baseline-rollout surface should preserve this order:

1. **What standing change is being proposed**
2. **Who and what will inherit it**
3. **What existing and future behavior will differ**
4. **What is explicitly excluded**
5. **How broad the rollout really is**
6. **Approve rollout, narrow cohort, split rollout, or reject**

### 1) What standing change is being proposed

The surface should name the baseline plainly.
Examples:

- `change default arrival root for members in cohort C`
- `change default single-file TTL for hosts in cohort H`
- `change global transfer-priority baseline for future shares on template T`

### 2) Who and what will inherit it

The product must enumerate the cohort in operator language.
Examples:

- `applies to these 6 named laptop hosts only`
- `applies to future offers issued from this workstation profile`
- `applies to new subjects published under template P, but not existing subjects`

### 3) What existing and future behavior will differ

This section must be example-backed.
Examples:

- `existing unchanged shares on hosts A/B/C would inherit priority P`
- `future single-file offers from workstation W would default to TTL 5 days`
- `future arrivals for member M would materialize under root R`
- `no already-adopted subjects are changed; future subjects only`

### 4) What is explicitly excluded

The operator should also see what the rollout will *not* touch.
Examples:

- `member exception E remains in force`
- `manual subject-level path overrides are preserved`
- `mobile members are excluded from this cohort`
- `existing offers already issued do not inherit the new TTL`

### 5) How broad the rollout really is

The surface should state the strongest honest breadth verdict:

- `single cohort, future-only`
- `single cohort, existing and future`
- `fleet-template mutation`
- `too broad for requested intent`

### 6) Approve rollout, narrow cohort, split rollout, or reject

The call to action should match reality:

- `Approve standing rollout`
- `Narrow target cohort`
- `Split into separate baselines`
- `Reject as wider than justified`

## Public rules

### Rule 1 — standing behavior must name its rollout cohort

No standing change may be justified only by where it is stored.
`host default`, `config file`, or `power-user setting` is not a cohort description.

### Rule 2 — future inheritance must be explicit

If future objects will inherit the change, the inheritance rule must be visible before approval.

### Rule 3 — exclusions are first-class

A rollout review that only lists what is included is incomplete.
The operator must also see preserved exceptions and non-targeted scopes.

### Rule 4 — example deltas are mandatory

At least one representative `existing` example and one representative `future` example should be shown whenever both are affected.

### Rule 5 — copied templates count as rollout scope

If a change spreads through configuration files, templates, or defaults reused across machines, that is a rollout even if no central controller is involved.

### Rule 6 — rollout approval is separate from standing classification

A change may correctly classify as standing scope and still be rejected because the proposed cohort is too wide.

## Dense row contract

A dense baseline-rollout row should preserve these labels in this order:

- `Baseline`
- `Target cohort`
- `Touches existing?`
- `Touches future?`
- `Explicit exclusions`
- `Breadth verdict`
- `State`

## Example prompts

- `Who exactly inherits this standing change?`
- `Does this touch existing subjects, future ones, or both?`
- `What is excluded from this rollout on purpose?`
- `Is this really a one-cohort change or a fleet mutation?`
- `What rollback boundary exists if the rollout proves too broad?`

## Anti-goals

- do not let `set the default` stand in for a real rollout description
- do not let copied configuration silently expand the cohort
- do not hide future inheritance inside template or preference names
- do not collapse preserved exceptions into undocumented footnotes
