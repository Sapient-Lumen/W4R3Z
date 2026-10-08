# Member policy editor and precedence ladder interface spec

## Purpose

The archive now has a member policy card that keeps future-arrival defaults public.
What still remained under-specified was the editing boundary itself:

> how does an operator change one member's future-arrival defaults without hiding precedence, confusing inheritance with explicit null, or letting one inline chip silently commit a semantic change that should have been reviewed?

This document defines the editor-side contract for member policy changes.
It is the action companion to `128-member-policy-card-and-future-arrival-default-review-interface-spec.md` and the precedence companion to `58-policy-origin-defaults-and-precedence-spec.md`.

## Core rule

Every semantic member-policy change must be prepared as an explicit **member policy edit plan** that renders:

1. the current effective defaults
2. the editable fields and their current inheritance mode
3. the precedence ladder that produces each field
4. example future-arrival simulations
5. explicit non-effects on current state
6. whether a wider publication-delta preview is required before apply

The member policy card may expose inline controls.
Those controls may not directly commit semantic policy changes.
They may only populate or revise a draft edit plan that remains inspectable before apply.

## Why this needs its own spec

Current Resilio docs still distribute future-arrival behavior across several surfaces and platform boundaries:

- `Synchronization Modes` and linked-device guidance define member-wide arrival posture
- `Sync Preferences` and related platform settings hold default folder behavior
- `Folder Preferences` remains a desktop-only place where treatment of synced material can change further
- manual-location and pre-populated-folder guidance teach operators to achieve desired outcomes through disconnect/connect ritual and remembered sequence

That is workable support-wise.
It is not one explicit edit contract.
AnonSync should instead make member-policy editing say, in one place, what is inheriting, what is pinned, what is merely suggested, what is future-only, and what wider review opens next.

## Public objects

### Member policy edit plan

A reviewed draft describing one proposed semantic edit to one member's future-arrival defaults.

Suggested fields:

- `member_policy_edit_plan_id`
- `member_ref`
- `current_member_policy_card_ref`
- `changed_field_plans[]`
- `simulation_case_refs[]`
- `requires_publication_delta_preview` boolean
- `non_effect_guarantees[]`
- `created_at`
- `expires_at` nullable

### Changed field plan

A compact explanation of one edited policy field.

Suggested fields:

- `changed_field_plan_id`
- `field_path`
- `current_effective_value`
- `requested_action` (`inherit`, `pin-value`, `pin-empty`, `clear-override`, `set-suggestion`, `set-exception-template`)
- `requested_value` nullable
- `precedence_before[]`
- `precedence_after[]`
- `conflict_flags[]`
- `future_only` boolean

### Simulation case

A representative example showing how a future arrival would be treated under the proposed member-policy edit.

Suggested fields:

- `simulation_case_id`
- `case_label`
- `subject_class`
- `current_predicted_outcome`
- `proposed_predicted_outcome`
- `difference_summary`
- `needs_delta_preview` boolean

### Member policy edit receipt

A durable proof that one reviewed edit plan was applied.

Suggested fields:

- `member_policy_edit_receipt_id`
- `member_policy_edit_plan_ref`
- `member_ref`
- `changed_fields[]`
- `delta_preview_ref` nullable
- `actor_ref`
- `created_at`
- `proof_refs[]`

## Fixed inspection order

Every member-policy-edit surface should preserve the same order:

1. **Member and current effective defaults**
2. **Fields being changed**
3. **Precedence ladder**
4. **Future-arrival simulations**
5. **What this edit does not rewrite now**
6. **Delta-preview boundary and apply gate**

### 1) Member and current effective defaults

This section should restate:

- which member is being edited
- its current future-arrival defaults
- current default roots or path suggestions
- whether important exceptions already exist

### 2) Fields being changed

Each semantic field must show:

- current effective value
- whether that value is inherited, pinned, empty by inheritance, or empty by pin
- requested new action
- whether the requested action is future-only or may touch current cells indirectly

### 3) Precedence ladder

This section is mandatory.
For every changed field, the surface must show the actual precedence chain, for example:

- built-in default
- profile or class template
- member-wide override
- subject-specific exception
- temporary lease, if one exists

The operator should never have to guess whether `clear` means `return to inheritance` or `pin to nothing`.

### 4) Future-arrival simulations

Every edit plan should show at least a few representative cases, such as:

- ordinary personal-document subject
- encrypted-only archival subject
- already exception-pinned subject class
- large-media subject using a different default root family

The simulation should keep `current predicted outcome` and `proposed predicted outcome` adjacent.

### 5) What this edit does not rewrite now

This section is mandatory.
Examples:

- does not move already claimed local paths
- does not promote current observer cells to writer
- does not erase subject-specific exceptions unless explicitly included
- does not silently refresh existing drafts unless that wider review is separately chosen

### 6) Delta-preview boundary and apply gate

If the edit can alter existing `(subject, member)` cells, the publication-delta preview must open before apply.
If the edit is provably future-only and touches zero existing cells, a compact review may be allowed — but it must still show the changed fields, precedence ladder, simulations, and receipt promise.

## Inline-edit boundary

### Rule 1 — inline controls may draft, not silently commit

A compact member card may let the operator toggle or type a new value inline.
That action may only populate or revise a draft edit plan.
It may not silently commit a semantic change.

### Rule 2 — semantic fields must expose inheritance state

Every editable semantic field must make `inherit`, `pin value`, `pin empty`, and `clear override` visibly distinct.

### Rule 3 — future-only does not mean explanation-free

Even when an edit provably touches zero existing cells, the product must still show a compact review with simulations and non-effects before apply.

### Rule 4 — precedence conflicts block compact apply

If exceptions, temporary leases, or imported policy layers create ambiguity, the compact flow must escalate to the full editor.

### Rule 5 — path suggestions stay subordinate to role/default posture

Default roots and path suggestions may be edited here, but they must remain visibly suggestions unless a later per-subject bind proves otherwise.

## Compact versus full review

The product may offer a **compact review sheet** only when all of the following are true:

- zero existing cells would change
- no subject-specific exceptions are being erased or narrowed
- no precedence conflict flags exist
- no authority widening occurs for current subjects

Otherwise the operator must be routed to the full editor and, when needed, onward to the publication-delta preview.

## Dense editor-row contract

A dense changed-field row should preserve these labels in this order:

- `Field`
- `Current`
- `Requested`
- `Inheritance`
- `Simulation effect`
- `Next`

## Acceptance test

The member-policy editor is good enough when a cautious operator can answer all of the following from one reviewed surface:

- what effective default is in force now for this member
- which field is being changed and whether the change inherits, pins, clears, or empties
- what precedence chain produced the current and proposed values
- how representative future arrivals would differ after apply
- what current state definitely will not be rewritten now
- whether a compact review is honest or a wider delta review is required
