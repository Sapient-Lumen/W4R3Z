# Remediation recipe catalog and reversibility review interface spec

## Purpose

The archive now has first-class surfaces for:

- convergence classification
- wait-vs-intervene judgment
- evidence bundles
- bounded intervention receipts
- diagnostic probe approval
- external escalation packet review

What still remained under-specified was the step between `we know more` and `we should act this way`.
In many real systems that step degenerates into support folklore:

- try opening a port
- switch a mode
- add a predefined host
- edit a hidden setting
- restart the service
- disable some security software for a moment
- run an external measurement tool
- hope the operator remembers how to undo it later

That is exactly the seam where AnonSync should refuse to clone Resilio-style troubleshooting ritual.
This document defines the interface contract for a first-class **remediation recipe catalog** and a **reversibility review** surface.

## Core rule

Any non-trivial operator action proposed in response to a sync, routing, publication, or arrival problem must be represented as a typed remediation recipe with:

1. the evidence that justifies it
2. the problem class it is trying to discriminate or fix
3. the expected positive and negative signals afterward
4. the collateral effects it may introduce
5. the exact rollback or expiry path
6. the proof obligation after it runs

The product must not force the operator to translate scattered troubleshooting prose into memory-driven side effects.

## Why this needs its own spec

Current Resilio help material is useful but still distributes actionable advice across many pages:

- open or forward the listening port
- allow direct connectivity or fall back to relay
- try predefined hosts
- use tracker or LAN discovery differently
- change `disk_low_priority`
- edit power-user preferences or config-mode fields
- collect or enlarge logs
- stop Sync and run `iperf3`

Those are all valid troubleshooting moves in context.
The problem is that they are not presented as one product-native recipe model with reversibility, scope boundaries, and post-action proof.
AnonSync should compile such moves into a catalog of typed recipes and make every recipe state its evidence target, blast radius, and rollback story before the operator commits it.

## Public objects

### Remediation recipe

A typed action plan that the product can recommend, preview, or stage.

Suggested fields:

- `remediation_recipe_id`
- `incident_ref`
- `recipe_kind` (`route-refresh`, `publication-reannounce`, `member-reachability-repair`, `default-policy-correction`, `path-rebind`, `local-resource-relief`, `diagnostic-precondition`, `external-measurement-prep`, `manual-network-change`, `service-restart`, `temporary-compatibility-toggle`)
- `goal_class`
- `justifying_evidence_refs[]`
- `preconditions[]`
- `proposed_scope`
- `collateral_risk`
- `reversibility_class` (`auto-expiring`, `one-click-rollback`, `manual-rollback`, `non-reversible-without-new-state`)
- `expected_positive_signals[]`
- `expected_negative_signals[]`
- `post_action_recompute_required` bool
- `approval_state` (`draft`, `reviewed`, `approved`, `running`, `finished`, `rolled-back`, `abandoned`)

### Recipe step row

One concrete step inside the recipe.

Suggested fields:

- `recipe_step_row_id`
- `step_index`
- `step_kind` (`inspect`, `change-setting`, `restart-local-agent`, `reissue-announcement`, `rebind-path`, `open-review`, `capture-measurement`, `manual-network-action`, `rollback-step`)
- `actor` (`product`, `operator`, `external-admin`)
- `requires_elevated_privilege` bool
- `requires_external_system` bool
- `can_be_undone` bool
- `summary`

### Reversibility row

One explicit statement about how the recipe can be undone or allowed to expire.

Suggested fields:

- `reversibility_row_id`
- `rollback_trigger`
- `rollback_deadline` nullable
- `rollback_path_summary`
- `residue_risk`
- `post_rollback_recompute_required` bool

### Proof obligation row

One statement of what must be checked after the recipe finishes.

Suggested fields:

- `proof_obligation_row_id`
- `proof_kind` (`convergence-verdict-change`, `route-directness-change`, `source-availability-change`, `member-observation-change`, `resource-pressure-change`, `no-effect-confirmed`)
- `freshness_requirement`
- `success_condition`
- `failure_interpretation`

## Fixed inspection order

Every recipe review surface should preserve this order:

1. **Why this recipe is justified now**
2. **What class of action it really is**
3. **Exact scope and collateral**
4. **Reversibility and expiry**
5. **What proof must be gathered afterward**
6. **Approve, run, schedule rollback, or reject**

### 1) Why this recipe is justified now

The surface should show the live evidence that selected the recipe.
Examples:

- `route is indirect and relay use is the strongest current bottleneck explanation`
- `member policy draft would correct future arrivals without touching current subjects`
- `local resource pressure is the strongest explanation for delayed settlement`
- `external measurement is now justified because ordinary route evidence is contradictory`

### 2) What class of action it really is

The product should not flatten every next move into the same verb.
It should say whether the recipe is:

- an observation refresh
- a local reversible change
- a standing-policy mutation
- a path or publication repair
- a manual network/environment change
- a diagnostic-precondition step for a later probe

### 3) Exact scope and collateral

This section should make explicit:

- which subject/member cells can change
- whether the action is future-only or touches live arrivals
- whether local runtime will restart or pause
- whether any external admin or router/firewall change is required
- whether collateral side effects may outlive the incident if rollback is skipped

### 4) Reversibility and expiry

The operator should see whether the recipe:

- auto-expires after the diagnostic window
- can be rolled back with one explicit product action
- requires manual undo outside the product
- cannot be fully reversed once new state is published or materialized

### 5) What proof must be gathered afterward

Every recipe must name the after-action check.
Examples:

- `recompute convergence verdict for these subject/member cells`
- `refresh direct-vs-relay route evidence`
- `confirm whether source availability is now fresh`
- `confirm no effect, then downgrade this hypothesis`

### 6) Approve, run, schedule rollback, or reject

The call to action should match the reversibility class.
Examples:

- `Approve and run`
- `Approve with automatic rollback in 20 minutes`
- `Stage manual network change and mark product-side follow-up required`
- `Reject recipe and choose safer alternative`

## Public rules

### Rule 1 — every recipe must be evidence-linked

A recipe cannot appear as pure folklore or habit.
The interface must name the evidence and hypothesis it answers.

### Rule 2 — the product must prefer the least-invasive viable recipe

If two recipes address the same uncertainty, the one with narrower scope and easier rollback should be preferred.

### Rule 3 — manual environment changes are a distinct class

Anything involving router settings, firewall policy, external host configuration, or third-party tools must be called out as an environment-changing recipe, not hidden among local product actions.

### Rule 4 — reversibility is part of the action, not a footnote

Rollback, expiry, and residue risk must appear before approval.

### Rule 5 — no recipe is complete without a proof obligation

Running a recipe without recomputing the relevant verdict is incomplete work.

### Rule 6 — no untyped `try this` actions

Freeform advice may exist as notes, but runnable actions must be modeled as recipes.

## Dense row contract

A dense recipe row should preserve these labels in this order:

- `Problem`
- `Recipe`
- `Scope`
- `Collateral`
- `Rollback`
- `Proof after run`
- `State`

## Example prompts

- `Why is this recipe better than just waiting?`
- `Which subject/member cells can this touch?`
- `Will this auto-expire or do I need to undo it?`
- `What will I look at afterward to know whether it worked?`
- `Is this a local product action or an external environment change?`

## Anti-goals

- no single undifferentiated `Advanced troubleshooting` drawer
- no irreversible changes hiding inside what looks like a harmless refresh
- no manual network or config surgery presented without residue warnings
- no recipe approval without a named rollback or non-reversibility explanation
- no after-action ambiguity about whether the recipe changed the live verdict
