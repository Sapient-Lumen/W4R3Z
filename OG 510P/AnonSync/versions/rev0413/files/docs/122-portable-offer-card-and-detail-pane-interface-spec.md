# Portable-offer card and detail-pane interface spec

## Purpose

The archive now has strong truth about:

- delivery provenance
- canonical artifact identity
- preview hints versus sealed fields
- preview sufficiency and omission truth
- preview/local-parse/claim decision ladders

The remaining risk is not conceptual.
It is layout risk.

> if the dense row and the full detail pane do not keep the same truths adjacent, the operator will still over-read convenience and forget what stayed missing.

This document defines the card/detail contract for portable offers.

## Core rule

A portable-offer row is not a teaser for a detail page.
It is itself a governance surface.

Every portable-offer row and every detail pane must keep six truths adjacent enough that the operator does not have to reconstruct them from memory:

1. what arrived
2. what was visible so far
3. what is still missing
4. what this is enough for
5. what it is not enough for
6. what the next honest action is

Receipts and proof links may be denser or more expandable, but those six truths must not fragment.

## Dense card anatomy

Every compact portable-offer row should preserve the same order:

1. **Identity strip**
2. **Visibility strip**
3. **Missing-governance strip**
4. **Decision-scope strip**
5. **Next-action strip**
6. **Receipt affordance**

### 1) Identity strip

This strip should answer `what is this?` with the strongest currently honest language.

Examples:

- `Offer: family-photos-2026`
- `Artifact: canonical id pending local parse`
- `Delivery: browser link`

This strip may include artifact label, canonical identity status, carrier class, or sender-intent cue when available.

### 2) Visibility strip

This strip should answer `what have I actually seen so far?`

Examples:

- `Visible now: label, approx size`
- `Visible now: parsed policy fields`
- `Visible now: preview only`

This is where preview familiarity gets bounded.

### 3) Missing-governance strip

This strip should answer `what still matters but is not available or not yet reviewed?`

Examples:

- `Missing: permissions, expiry`
- `Missing: claim review`
- `Missing: approval seat choice`

Do not hide this in a tooltip.

### 4) Decision-scope strip

This strip should answer two paired questions in one place:

- enough for what?
- not enough for what?

Examples:

- `Enough for: recognition`
- `Not enough for: accept`

or

- `Enough for: inspect`
- `Not enough for: apply`

### 5) Next-action strip

This strip should give one primary truthful next action.
Examples:

- `Inspect locally`
- `Prepare claim`
- `Request narrower reissue`
- `Keep at recognition only`

### 6) Receipt affordance

This strip may be visually lighter, but it should remain present.
Examples:

- `Show receipts`
- `1 proof link`
- `Ladder receipt pending`

## Full detail-pane anatomy

Every full pane should preserve the same section order:

1. **What arrived**
2. **What was visible at each step**
3. **What is missing or still blocked**
4. **What this is enough for now**
5. **What this is not enough for yet**
6. **Decision ladder and next action**
7. **Receipts and proof links**

### What arrived

This section should show:

- delivery channel
- carrier alias if relevant
- canonical offer identity status
- sender-intent cue when available
- artifact lineage if the offer is a reissue or successor

### What was visible at each step

This section should keep preview, parse, and claim stages distinct.
For example:

- browser preview showed label and approximate size
- local parse revealed expiry and use-count policy
- claim draft selected local path and role

### What is missing or still blocked

This section should state omitted or still-unreviewed truth plainly.
This includes both field omissions and process omissions.

### What this is enough for now

This section should state current positive scope.
Examples:

- recognition only
- routing hint only
- local inspection
- claim drafting

### What this is not enough for yet

This section should state the blocked domains.
Examples:

- not enough for durable trust
- not enough for approval reuse
- not enough for apply

### Decision ladder and next action

This section should include the current rung and the primary next action in one visible block.

### Receipts and proof links

This section should show delivery, alias, field-partition, sufficiency, ladder, claim, and promotion receipts when relevant.

## Cross-surface rules

### Rule 1 — the dense row must not contradict the full pane by omission

The detail pane may elaborate.
It must not be the first place where the user learns that permissions or claim review are still missing.

### Rule 2 — the dense row must survive color loss

Do not depend on color alone for `recognition only`, `review needed`, or `blocked`.
Text must carry the meaning.

### Rule 3 — mobile compaction must preserve adjacency, not delete truth

On narrow screens the product may stack strips vertically.
It may not move `missing` three scroll lengths away from `next action`.

### Rule 4 — sorting and batching must use the same fields users see

If the interface can sort by urgency or readiness, it should do so using the same explicit ladder, omission, and next-action fields that the user can inspect.

## Allowed and forbidden microcopy

### Allowed

- `Preview only`
- `Parsed, review still needed`
- `Enough for: recognition`
- `Missing: expiry, claim review`
- `Next: inspect locally`

### Forbidden

- `Looks good`
- `Known share`
- `Ready`
- `Safe to connect`
- `Continue`

## Workbench lane expectations

Offer cards in the workbench should be batchable only when their decision scope matches.
The operator should not batch-apply a mix of:

- preview-only rows
- parsed-but-unreviewed rows
- claim-prepared rows

without one review surface explicitly naming that mixed posture.

## CLI/TUI parity

Textual surfaces should preserve the same adjacency using fixed labels, for example:

```text
What arrived: browser link, canonical id pending parse
Visible now: label, approx size
Missing: permissions, expiry
Enough for: recognition
Not enough for: accept
Next: inspect locally
```

## Acceptance test

The card/detail contract is good enough when a cautious operator can glance at either surface and answer all of the following within one visual group:

- what arrived
- what they have really seen
- what is still missing
- what decision scope is currently honest
- what next move is honest
