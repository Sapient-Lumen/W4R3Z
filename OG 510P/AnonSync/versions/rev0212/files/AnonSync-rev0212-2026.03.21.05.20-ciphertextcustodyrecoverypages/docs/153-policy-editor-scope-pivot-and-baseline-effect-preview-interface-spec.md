# Policy editor, scope pivot, and baseline-effect preview interface spec

## Purpose

This document decides what happens when an operator moves from `I understand this value` to `I want to change it`.
That transition is where many sync products start hiding scope.
The question is not merely `how do we edit a field?`
The real question is:

> what interface object forces the operator to choose the right mutation instrument before a value edit silently turns into baseline drift, local pinning, or a special case that no one can later explain?

This is one of the clearest non-clone responses to the current Resilio evidence.
Several current Resilio docs remain useful, but they still imply a world where behavior may come from folder preferences, sync preferences, power-user defaults, config mode, or support ritual depending on what was touched before.
AnonSync should not let `edit` hide that fork.

## Core decision

Every non-trivial value edit must begin with a **scope pivot sheet**.
This sheet appears before the operator edits the value itself unless the product can already prove only one mutation instrument is legal and honest.

The scope pivot must answer four questions first:

1. **What is the current source of this value?**
2. **What kind of change is the operator trying to make?**
3. **What scope will this change actually touch?**
4. **What will happen later if the parent baseline changes again?**

Only after those are explicit may the field editor open.

## Allowed mutation instruments

The pivot should make these instruments first-class choices where relevant:

### `edit-baseline`

Change the governing baseline or defaults profile for all still-inheriting dependents.

### `pin-here`

Detach this one subject from parent change and set a direct local value.
This is intentionally treated as a special act, not a casual inline tweak.

### `temporary-override`

Create a leased divergence with explicit end condition.
The operator is not just changing a value; they are creating a time- or condition-bounded exception.

### `durable-exception`

Create or extend a reviewed exception object.
This is a governance act, not merely a local customization.

### `restore-inheritance`

Remove a pin or end an exception so the subject follows its parent again.

### `inspect-only`

Open the explanation drawer when the operator realized they still do not understand the value origin.

## Things the editor should refuse

The product should refuse these interface habits:

- one vague `Customize` button that mixes baseline edits, local pins, exceptions, and leases
- value entry fields that open before the operator has chosen scope
- inline edits that look local but actually widen to all inheriting dependents
- baseline edits whose real blast radius is hidden in a later confirmation footer
- `restore defaults` wording that hides whether the subject will truly inherit again or merely copy the current baseline statically

## Scope pivot anatomy

A good pivot sheet should keep one fixed order.

### 1) Subject and acting-seat banner

Show:

- current subject
- current acting seat
- property label
- current effective value
- current source state

This is the answer to `what am I editing, from which authority position?`

### 2) Current source explanation

A compact summary should say things like:

- `Inherits from Family baseline`
- `Pinned locally on this member`
- `Temporary override active until 18:00`
- `Durable exception approved by Storage stewards`
- `Copied static from import profile`

This is the answer to `what would I be changing away from?`

### 3) Instrument chooser

Render the allowed mutation instruments as mutually exclusive choices, each with:

- scope summary
- future baseline behavior summary
- review tier
- whether a new draft object will be required

The operator should be able to compare `pin here` against `durable exception` before committing.

### 4) Blast-radius preview

Before field editing, show the affected set in plain language:

- `Touches 17 inheriting members`
- `Touches only this subject`
- `Creates an exception for 1 subject and leaves 17 still inheriting`
- `Restores 4 subjects to baseline on lease expiry`

### 5) Future baseline effect preview

The sheet must explicitly classify the downstream future into at least:

- will follow future parent changes
- will no longer follow future parent changes
- will rejoin automatically at lease end
- will require later review to rejoin
- cannot be predicted safely yet

This is one of the most important sections.
A present-tense diff is not enough.

### 6) Field editor

Only after the instrument choice is explicit should the actual field editor appear.
The editor may be inline or on a second step.
The important part is that the semantic fork has already been made.

### 7) Resulting object summary

Before apply, the surface should say whether the action creates:

- a baseline draft
- a local pin receipt
- a temporary override lease
- a durable exception draft
- a restore-inheritance draft or receipt

## Review-boundary rules

### Baseline edits

Baseline edits almost always require a preview of affected dependents and therefore generally produce a draft object.
Direct apply is only acceptable for truly local private cases with no hidden dependents.

### Local pins

Local pins may direct-apply only when their scope is provably one subject, their risk tier is low, and their effect on future inheritance is stated in-line.
Otherwise they produce a draft.

### Temporary overrides and durable exceptions

These always create reviewable objects.
The operator is not just changing a number; they are changing governance.

### Restore inheritance

Restore may direct-apply when no blockers remain and the resulting post-state is simple.
If any blockers remain, such as overlapping exceptions or incompatible current observations, restore should open a review object instead.

## Dense and narrow surfaces

### Dense tables

A table row may open the pivot in a side sheet.
It should not open a raw field editor immediately just because space is tight.

### Narrow/mobile surfaces

Narrow surfaces may merge source explanation and instrument chooser into one stacked sheet.
They may not omit the blast-radius and future-baseline sections.

## Result

A good scope pivot prevents five common mistakes:

- changing a baseline when the operator only meant to special-case one subject
- pinning a subject when the operator really meant a leased override
- mistaking `restore defaults` for real inheritance restoration
- editing a value without seeing what future baseline changes will or will not do
- discovering only after apply that the action created a governance object rather than a local tweak

If the first edit affordance is the field itself, the interface is already too loose for AnonSync.
