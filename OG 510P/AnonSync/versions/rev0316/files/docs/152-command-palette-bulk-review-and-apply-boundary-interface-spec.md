# Command palette, bulk review, and apply-boundary interface spec

## Purpose

This document decides how AnonSync should support fast keyboard-driven access and bulk action without hiding scope.
The question is not `should the product be fast?`
The answer to that is yes.
The real question is:

> how far may speed features go before they start acting like hidden authority?

## Core decision

The command palette is allowed to accelerate:

- navigation
- explanation
- search
- safe read actions
- draft creation
- low-risk local actions with obvious scope

The command palette is **not** allowed to become a hidden bypass for trust-expanding, destructive, topology-changing, or exception-creating mutations.
For those, it may start the flow, but it must land in a normal review object inside the shell.

## Palette modes

A single omnibox may support these broad intents:

### `jump`

Open a subject, report, offer, receipt, or page.

### `explain`

Open a proof drawer, value explanation, or audit trail.

### `draft`

Create a claim draft, exception draft, plan draft, or review bundle.

### `act-safe`

Run a low-risk action whose scope is already obvious from the current page and does not widen trust or destroy shared state.
Examples might include local expand/collapse, refresh proof, or open compare.

### `help`

Show available verbs, filters, and shortcuts.

## Things the palette should refuse to direct-apply

The palette should not direct-apply these classes of actions:

- share-wide delete
- trust widening
- approval-memory reuse changes
- exception creation
- baseline edits
- non-empty-path bind
- route/discovery widening
- any multi-subject action with mixed proof or mixed risk class

For those actions, the palette should instead open the relevant review object already populated with the intended scope.

## Batch admissibility test

Direct bulk apply is only allowed when every selected subject matches on all of the following:

1. **same action kind**
2. **same subject family**
3. **same scope class**
4. **same risk tier**
5. **compatible proof freshness**
6. **no material outlier blocker or warning**

If any one of those fails, the interface must split the batch or fall back to draft/review.

## Outlier handling

Outliers should never hide in a footer warning.
A batch preview should explicitly show:

- common-case count
- outlier count
- outlier reason groups
- the resulting split plan

Example:

- `12 rows selected`
- `9 can refresh directly`
- `2 need fresh convergence proof`
- `1 blocked by active exception expiry conflict`

From there the operator may:

- apply the safe subgroup
- open one combined draft for the review-required subgroup
- inspect the blocked outlier separately

## Batch preview anatomy

A batch preview should always contain:

1. selected count
2. common action summary
3. common scope summary
4. explicit split/outlier section
5. proof freshness summary
6. resulting receipts summary

If the batch is too heterogeneous to summarize honestly, the interface should refuse the direct preview and offer to create review objects instead.

## Receipt rules

A bulk receipt should preserve:

- which subjects were in the original selection
- which subjects executed together
- which subjects split out and why
- which subjects were blocked
- the proof or review objects referenced by each subgroup

This matters because a safe bulk model is not just about preventing mistakes.
It is also about preserving legible aftermath.

## Keyboard and textual parity

CLI and TUI projections should be able to express the same distinctions, even if they do not expose a graphical omnibox.
That means textual surfaces should still support:

- draft instead of direct apply for risky commands
- machine-readable split reasons
- subgroup apply receipts
- explicit blocked/outlier lists

## Result

A good speed model should let advanced operators move quickly without making the product ambiguous.
The operator should not be left wondering:

- `did that shortcut just widen scope?`
- `did the bulk action silently skip or flatten a warning?`
- `was that action applied directly or merely drafted for review?`
- `which row was the odd one out and where did it go?`

If the answer is unclear, the speed model is too aggressive.
