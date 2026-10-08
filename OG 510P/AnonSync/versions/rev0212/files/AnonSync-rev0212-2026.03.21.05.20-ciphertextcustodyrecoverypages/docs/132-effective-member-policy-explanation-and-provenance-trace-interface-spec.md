# Effective member policy explanation and provenance trace interface spec

## Purpose

The archive now has:

- member policy cards
- draft-first member-policy editing
- mutation ledgers for publication changes
- impact proofs for member-policy edits

What still remained under-specified was the operator's simplest ongoing question:

> why does this member currently have these future-arrival defaults, and which mutation, inheritance layer, exception, or temporary lease made that true?

This document defines the explanation surface for current effective member policy.
It is the ongoing-state companion to `128-member-policy-card-and-future-arrival-default-review-interface-spec.md` and the post-apply companion to `130-member-policy-editor-and-precedence-ladder-interface-spec.md`.

## Core rule

For any member, the product must be able to render one explicit **effective member policy explanation** object that shows, field by field:

1. the current effective value
2. the provenance chain that produced it
3. whether the value is durable or temporary
4. which recent mutation most recently changed it
5. what representative future arrivals this value influences

The operator should not need to open preferences, remember edit history, or infer precedence from the fact that some later arrival happened a certain way.

## Why this needs its own spec

Current Resilio docs still distribute default-arrival behavior across synchronization modes, preference surfaces, folder preferences, and reconnect/custom-location guidance.
That can be learned.
But it still makes everyday explanation feel like folklore:

- why did this member get `Disconnected` by default
- why is the default root here instead of there
- why did a later arrival inherit observer instead of writer
- which change actually caused the current outcome

AnonSync should answer those questions from one explanation object, not from remembered ritual.

## Public objects

### Effective member policy explanation

A current-state explanation object for one member.

Suggested fields:

- `effective_member_policy_explanation_id`
- `member_ref`
- `generated_at`
- `field_explanation_rows[]`
- `active_temporary_modifier_refs[]`
- `recent_mutation_refs[]`
- `representative_outcome_refs[]`
- `freshness_class`

### Field explanation row

A field-level explanation for one effective default.

Suggested fields:

- `field_explanation_row_id`
- `field_path`
- `effective_value`
- `durability_class` (`durable`, `temporary`, `pending-replacement`)
- `precedence_chain[]`
- `winning_source_ref`
- `most_recent_change_ref` nullable
- `representative_effect_summary`

### Provenance step

One step in the chain that explains why a field won.

Suggested fields:

- `provenance_step_id`
- `source_kind` (`built-in-default`, `class-template`, `member-override`, `subject-exception-template`, `temporary-lease`, `incident-freeze`, `successor-carry-forward`)
- `source_ref`
- `value_if_selected`
- `selected` boolean
- `non_selection_reason` nullable

### Effective policy explanation receipt

A durable exportable proof of the explanation rendered at a point in time.

Suggested fields:

- `effective_policy_explanation_receipt_id`
- `effective_member_policy_explanation_ref`
- `generated_for_actor_ref`
- `created_at`
- `evidence_hash`
- `included_recent_mutation_refs[]`

## Fixed inspection order

Every effective-policy explanation surface should preserve this order:

1. **Member summary and freshness**
2. **Effective defaults now**
3. **Provenance ladder by field**
4. **Temporary modifiers and expiry truth**
5. **Recent mutations that changed today's state**
6. **Representative future-arrival outcomes**
7. **Next honest actions**

### 1) Member summary and freshness

This section should show:

- member identity and class
- current freshness of the explanation
- whether there are pending edits not yet applied
- whether any active temporary policy is masking the durable baseline

### 2) Effective defaults now

This section should answer, in plain operator language:

- default role posture for future arrivals
- default arrival/materialization posture
- default root or path-suggestion family
- default exception template, if any

### 3) Provenance ladder by field

Every semantic field must render its full ladder, for example:

- built-in default
- class template
- durable member override
- subject-family exception template
- temporary lease or incident freeze

The winning source should be visually marked.
Losers should still show why they lost, such as `overridden later`, `lease expired`, or `suppressed by incident posture`.

### 4) Temporary modifiers and expiry truth

Temporary state must not masquerade as durable policy.
If a field currently wins because of a lease or incident freeze, the surface must show:

- what durable value would win without the modifier
- what temporary value wins now
- when or how the temporary state ends
- whether expiration auto-restores the durable value or demands rereview

### 5) Recent mutations that changed today's state

Operators should be able to ask `what changed recently?` without leaving the explanation surface.
This section should show the most relevant mutation receipts that changed the current effective state, such as:

- a member-policy edit receipt
- a publication template change
- a temporary lease grant or expiry
- a successor or incident-driven freeze

### 6) Representative future-arrival outcomes

Explanation is only complete when it shows practical consequences.
This section should keep example outcomes adjacent, such as:

- ordinary personal document arrival
- archival arrival
- high-risk incoming offer
- path-sensitive media subject

For each case, the surface should say what the member would get now and which field values caused that result.

### 7) Next honest actions

Only actions supported by current evidence should appear, for example:

- `Open editor`
- `Compare with previous explanation`
- `Export explanation receipt`
- `Inspect active lease`
- `Inspect last mutation`

## Public rules

### Rule 1 — explanation is a first-class object, not a reconstruction ritual

The product must expose the explanation directly rather than forcing operators through settings, history, and support pages.

### Rule 2 — temporary winners must name the durable loser underneath

A temporary modifier is only honest when the durable baseline remains visible beneath it.

### Rule 3 — recent mutation trace must stay adjacent to current truth

Operators should not have to jump into an audit ledger just to learn which recent change made today's value win.

### Rule 4 — representative outcomes are mandatory

Pure precedence diagrams are not enough.
At least a few example arrival outcomes must be shown so the operator can connect the abstract defaults to real behavior.

### Rule 5 — explanation receipt does not freeze future truth

An explanation receipt proves what the system rendered at one time.
It does not guarantee that the same defaults remain true after later mutations or expiry.

## Dense row contract

A dense field explanation row should preserve these labels in this order:

- `Field`
- `Effective now`
- `Winner`
- `Why`
- `Recent change`
- `Representative effect`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following from one explanation object:

- what this member's current future-arrival defaults actually are
- which provenance layer won for each important field
- whether any temporary state is masking the durable baseline
- which recent mutation most recently changed today's posture
- how those defaults would influence a few representative future arrivals
