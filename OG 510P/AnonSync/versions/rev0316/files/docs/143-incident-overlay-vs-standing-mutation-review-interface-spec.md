# Incident overlay vs standing mutation review interface spec

## Purpose

The archive now has first-class surfaces for:

- evidence bundles and disambiguation ladders
- remediation recipe catalogs and reversibility review
- external guidance intake and translation review

What still remained under-specified was a dangerous branch inside remediation itself:

- is this proposal a narrow, incident-bounded overlay?
- or is it a standing mutation that will keep affecting future arrivals, future publications, future downloads, or even other machines?

That distinction is exactly where real systems often leak operator intent.
A suggestion that began as `just unblock this one incident` quietly becomes:

- a new global default
- a member-wide future-arrival rule
- a host-wide transport preference
- a config file copied to many machines
- a share default that keeps affecting future material

This document defines the interface contract for making that distinction explicit before any recipe is approved.

## Core rule

Every remediation recipe that changes ongoing behavior must be classified as one of these two kinds before approval:

1. **incident overlay** — a bounded temporary override justified by one incident and expected to expire, roll back, or be removed
2. **standing mutation** — a durable policy, preference, template, or host-level change that will keep influencing future state until changed again

The product must not let a wide-scope standing mutation masquerade as a quick incident fix.

## Why this needs its own spec

Current Resilio docs sharpen this boundary in a way that is genuinely useful to study.

They currently document:

- member-wide synchronization modes that govern how newly added folders arrive
- a default folder location used when a device is in `Selective Sync` or `Synced`
- share-level `Folder Preferences` that can require tracker, relay, LAN search, or predefined hosts behavior
- power-user preferences that expose global knobs like log size and profiler capture
- a newer global `folder_defaults.transfer_priority` setting that can automatically affect existing unchanged shares and future shares
- configuration mode specifically described as a way to apply pre-configured parameters across a number of different machines

None of those controls are illegitimate.
The problem is that they create exactly the kind of scope drift AnonSync should surface directly:

- one incident-level performance or reachability hypothesis can turn into a durable host default
- one share-level fix can silently become a future-share default
- one machine-local tweak can become a fleet pattern by config replication

AnonSync should therefore force every such action through an explicit **overlay-vs-standing** review before approval.

## Public objects

### Scope classification object

The durable object that states what kind of change this really is.

Suggested fields:

- `scope_classification_id`
- `incident_ref`
- `origin_recipe_ref`
- `scope_class` (`incident-overlay`, `standing-mutation`, `mixed-with-split-required`)
- `evaluation_state` (`draft`, `reviewed`, `approved`, `rejected`)
- `strongest_reason`
- `future_effects_summary`
- `rollback_expectation`
- `requires_split_before_run` bool

### Overlay candidate row

One claim that the proposal can be bounded to the incident.

Suggested fields:

- `overlay_candidate_row_id`
- `candidate_name`
- `bounded_dimension` (`time`, `subject-set`, `member-set`, `host`, `network-scope`, `diagnostic-window`)
- `bounded_value`
- `expiry_or_stop_condition`
- `collateral_beyond_incident` (`none-known`, `possible`, `certain`)
- `confidence`

### Standing effect row

One way the proposal would continue affecting future behavior.

Suggested fields:

- `standing_effect_row_id`
- `effect_kind` (`future-arrival-default`, `future-publication-behavior`, `share-default`, `host-runtime-default`, `fleet-config-default`, `diagnostic-default`, `download-order-default`)
- `affected_scope`
- `would_touch_existing_objects` bool
- `would_touch_future_objects` bool
- `explanation`

### Split recommendation row

One suggested split when the current proposal mixes temporary and standing parts.

Suggested fields:

- `split_recommendation_row_id`
- `unsafe_mixed_piece_summary`
- `recommended_overlay_piece`
- `recommended_standing_piece`
- `why_split_is_required`

## Fixed inspection order

Every overlay-vs-standing review surface should preserve this order:

1. **What problem this recipe is trying to answer**
2. **What ongoing behavior would actually change**
3. **Why this counts as overlay, standing mutation, or mixed**
4. **How to narrow it if the scope is too wide**
5. **What future state would differ if approved**
6. **Approve narrow overlay, approve standing mutation, split, or reject**

### 1) What problem this recipe is trying to answer

The surface should restate the incident trigger and evidence basis.
Examples:

- `route evidence suggests direct-connect failure on one member`
- `download ordering is causing unacceptable local settlement delay`
- `future arrivals are landing in an unsafe default root`

### 2) What ongoing behavior would actually change

This section must answer the quiet part directly.
Examples:

- `applies only to the current convergence window`
- `changes how future subjects arrive for this member`
- `changes default transfer priority for future shares and some existing unchanged shares`
- `changes launch-time parameters for every machine using this config file`

### 3) Why this counts as overlay, standing mutation, or mixed

The product should show the strongest current classification:

- `incident overlay because the proposal expires after one bounded measurement window`
- `standing mutation because it changes host defaults until explicitly changed again`
- `mixed because the requested fix combines a temporary route override with a durable folder-default change`

### 4) How to narrow it if the scope is too wide

The product should suggest splits such as:

- keep the route override incident-bounded, reject the standing host default
- keep the measurement window temporary, reject the persistent profiler toggle
- create a subject/member exception instead of mutating a member-wide future default
- create a one-share override instead of changing a fleet config template

### 5) What future state would differ if approved

This is mandatory.
The operator should see examples like:

- `these future arrivals for member M would now materialize under root R`
- `new shares created on this host would inherit transfer priority P`
- `all machines launched from config template T would inherit parameter X`
- `no future state would differ after the incident closes`

### 6) Approve narrow overlay, approve standing mutation, split, or reject

The call to action must match the classification:

- `Approve overlay with lease`
- `Approve standing mutation`
- `Split into overlay + standing draft`
- `Reject as unjustifiably wide`

## Public rules

### Rule 1 — standing scope must be declared before approval

No recipe may smuggle in a future-default effect as collateral.

### Rule 2 — the product must prefer the narrowest effective scope

If the incident can be addressed by a lease, exception, or per-subject/member override, that should be preferred over a standing host or fleet mutation.

### Rule 3 — mixed recipes require split review

If one draft combines temporary and standing parts, the product must either split them or force the operator to approve each part explicitly.

### Rule 4 — future examples are required

A standing mutation review must show at least one representative future outcome that would differ.

### Rule 5 — config replication counts as standing scope

Any change that propagates through templates, config files, or copied defaults must be labeled as standing even if the operator first encountered it during one incident.

### Rule 6 — `until we remember to undo it` is not an overlay

A temporary intent without a lease, stop condition, or rollback plan is not bounded enough.

## Dense row contract

A dense overlay-vs-standing row should preserve these labels in this order:

- `Change`
- `Current classification`
- `Touches existing?`
- `Touches future?`
- `Narrower alternative`
- `Lease/rollback`
- `State`

## Example prompts

- `Is this really just an incident fix, or will it keep changing future arrivals?`
- `What future shares or members would inherit this if I approve it?`
- `Can the product split the temporary part from the durable default?`
- `Why is this being labeled standing scope instead of overlay?`

## Anti-goals

- do not hide durable effects behind words like `temporary`, `advanced`, or `for troubleshooting`
- do not make operators infer scope from config location alone
- do not let future defaults change without one explicit review surface
- do not flatten host-wide, member-wide, share-wide, and fleet-wide scope into one generic `setting changed` event
