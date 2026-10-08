# Draft object summary, outlier split, and apply interface spec

## Purpose

This document decides what non-trivial work becomes before it becomes state.
The archive already says many risky or wide-scope actions should not direct-apply from a palette or inline row.
This document adds the missing positive object:

> what durable thing should exist between intent and apply so the operator can inspect scope, proof, outliers, and expected receipts in one place?

That thing is the **draft object**.

## Core decision

Any non-trivial mutation should compile into a first-class draft object unless the product can prove safe direct-apply without hidden scope.
The draft object is not a temporary modal.
It is a stable, linkable, receipt-adjacent subject.

A draft object must preserve:

- action kind
- selected subject set
- scope class
- risk tier
- proof freshness summary
- outlier groups and split plan
- predicted receipts or resulting objects
- current blockers

## What counts as non-trivial here

Examples include:

- baseline edits
- durable exceptions
- temporary overrides
- publication changes affecting multiple members
- bind/adopt work on non-empty or ambiguous targets
- discovery/route widening
- destructive replay or retained-copy recall
- any batch where rows diverge materially in blockers, freshness, or scope

## Draft object anatomy

### 1) Header

Must show:

- draft label and stable handle
- action kind
- acting seat
- created time and freshness state

### 2) Current intention summary

One sentence should say what the operator is trying to do, for example:

- `Raise baseline fetch budget for all still-inheriting travel peers.`
- `Create a temporary override permitting LAN-only direct path until tomorrow 09:00.`
- `Restore these four subjects to inheritance, except one blocked outlier.`

### 3) Scope summary

This region must name:

- subject family or families
- selected count
- effective apply groups
- whether the draft spans one subject, one cohort, or mixed cohorts

### 4) Proof freshness summary

The draft should state whether supporting proof is:

- fresh enough to apply
- still usable but nearing expiry
- stale and review-required
- incomplete because blockers remain

### 5) Outlier and split section

This is the heart of the draft.
It should show:

- common-case group count
- outlier groups by reason
- blocked items
- resulting execution plan

Example:

- `12 selected`
- `8 can apply as one baseline edit`
- `3 need fresh member-policy proof`
- `1 is blocked by overlapping temporary override`

The operator may then choose to:

- apply the common safe subgroup
- hold the entire draft
- split into subgroup drafts
- inspect blocked outliers individually

### 6) Predicted aftermath

Before apply, the draft should say what artifacts or receipts are expected:

- one baseline receipt
- one override lease and two restore receipts
- three subgroup receipts plus one blocked remainder
- one disclosure receipt and one export manifest

### 7) Apply region

The apply region must keep safe/default action and danger action separate.
It should also preserve why direct-apply is or is not currently allowed.

## Split rules

### Automatic split is allowed when

The system can prove that rows diverge for reasons that change safe execution.
Examples:

- proof freshness mismatch
- blocker mismatch
- risk-tier mismatch
- scope-class mismatch
- overlapping lease or exception conflicts

### Automatic split is not allowed when

The split itself would hide an important operator choice.
For example, if some subjects would be widened by baseline edit and others would instead require durable exceptions, the system should not silently split and proceed; it should ask the operator to confirm the different instruments.

## Lifecycle rules

A draft object may move through these states:

- `assembled`
- `needs-proof-refresh`
- `blocked-partially`
- `ready-to-apply`
- `applied-partially`
- `applied`
- `superseded`
- `cancelled`

These states matter because the operator should be able to reopen a draft later without guessing whether it is still actionable.

## Cross-surface rules

A draft object must be deep-linkable and projection-neutral.
That means GUI, local web, TUI, and CLI can all:

- list drafts
- open a draft
- inspect subgroup splits
- refresh proof
- apply or cancel when authorized

No projection may reduce drafts to hidden local state if another projection would present them as durable review objects.

## Result

A good draft object prevents four expensive mistakes:

- applying a heterogeneous batch as though it were one uniform act
- discovering blockers only after partial state mutation has already happened
- losing the original intent because the operator had to leave the page to inspect outliers
- forgetting later whether a stalled plan was never applied, partially applied, or superseded

If non-trivial work exists only as button press plus eventual receipts, the product is still too magical.
