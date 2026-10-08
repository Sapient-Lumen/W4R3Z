# Approval-memory freshness, cooling, and touch-renewal interface spec

## Purpose

The archive already separates first approval from later remembered matches, explains later-arrival causality, previews standing-policy edits, traces policy lineage, classifies drift, and ages intentional exceptions.
One gap still remained: **remembered approval itself** can outlive the conditions that originally made it feel safe.

This document turns that question into one explicit interface contract.
It is the freshness companion to `97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md`, the dormancy companion to `70-dormant-peer-reentry-and-stale-state-review-spec.md`, the lifecycle companion to `105-exception-aging-renewal-and-rereview-interface-spec.md`, and the posture companion to `107-approval-memory-lineage-and-authorization-trace-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Sync functionality in detail`, `Sync Private Identity & Linking My Devices`, `Folder Types and Management`, `User Management`, and `What's the difference between Standard and Advanced folders?` together still describe a system where:

- approving a person once can remain enough for later sharing because approval is retained with their identity
- a remote user can choose to automatically approve all linked devices for future sharing after approving one
- pending folders can automatically connect if that user approved you before
- linked devices under one identity act as Owners
- current help explains how remembered approval works, but not one first-class freshness lifecycle for when old trust should cool, freeze, or demand touch renewal

That is real convenience.
It is not yet one trustworthy contract for long-lived remembered trust.
A remembered approval that was sensible after a fresh collaboration window is not automatically equally appropriate after long dormancy, identity rotation, linked-device growth, role change, or repeated no-shows.

AnonSync should not accept immortal convenience memory here.
Any standing approval memory that can influence later arrivals should therefore also surface one explicit **freshness, cooling, and touch-renewal contract**.

## Core rule

Remembered approval is not timeless.

The product is not fully inspectable until it can answer six questions in one place:

1. what remembered approval still exists for this peer, share class, or governed scope
2. when it was last explicitly reviewed and last actually exercised
3. what facts are currently cooling, narrowing, or freezing that memory
4. what the current freshness class permits and forbids for later arrivals
5. which reviewed outcomes are available now (`touch-renew`, `narrow`, `freeze`, `require-fresh-approval-next-time`, or `revoke`)
6. which receipt later proves that the product merely refreshed trust memory, narrowed it, or stopped reusing it

If the operator still has to combine old approval receipts, arrival history, and private memory to decide whether remembered trust is still fresh enough to reuse, the surface is not explicit enough.

## Public objects

### Approval-memory freshness row

A compact read object describing one remembered approval's current trust-freshness posture.

Suggested fields:

- `approval_memory_freshness_row_id`
- `approval_memory_ref`
- `seat_ref`
- `governed_scope`
- `granted_scope_summary`
- `last_explicit_review_at` nullable
- `last_exercised_at` nullable
- `freshness_class` (`fresh`, `warm`, `cooling`, `stale`, `frozen`, `revoked`, `unknown`)
- `cooling_reasons[]`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Approval-memory freshness population

A read object summarizing current remembered-trust freshness for one seat/scope.

Suggested fields:

- `approval_memory_freshness_population_id`
- `seat_ref`
- `governed_scope`
- `summary_counts`
- `freshness_rows[]`
- `generated_at`
- `generation_basis` (`live`, `cached`, `receipt-reconciled`)

### Approval-memory touch-renewal plan

A prepared mutation object for one reviewed attempt to refresh, narrow, freeze, or retire remembered approval.

Suggested fields:

- `approval_memory_touch_renewal_plan_id`
- `approval_memory_ref`
- `seat_ref`
- `governed_scope`
- `current_freshness_class`
- `requested_outcome` (`touch-renew`, `narrow-scope`, `freeze-reuse`, `require-fresh-approval-next-time`, `revoke-memory`)
- `proposed_scope_delta` nullable
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Approval-memory freshness receipt

A durable object proving the result of one remembered-trust freshness review.

Suggested fields:

- `approval_memory_freshness_receipt_id`
- `approval_memory_ref`
- `seat_ref`
- `previous_freshness_class`
- `outcome`
- `reviewed_at`
- `next_expected_review_at` nullable
- `result_scope_summary`
- `proof_refs[]`

## Freshness classes

Every remembered approval that can influence later arrivals should map to one explicit freshness class.

### `fresh`

Use when remembered approval was reviewed or exercised recently enough that ordinary reuse remains within policy.

### `warm`

Use when remembered approval is still comfortably reusable, but the product wants the operator to see that the next long silence could move it toward cooling.

### `cooling`

Use when dormancy, scope drift, or topology change has begun to undermine confidence.
Cooling must stay reusable only if policy allows it, and the row must explain exactly what will happen on the next arrival.

### `stale`

Use when remembered approval is too old or too changed to keep acting like quiet convenience memory.
A stale row should usually force one reviewed freshness outcome before later arrivals reuse it broadly.

### `frozen`

Use when remembered approval remains visible as historical evidence but is no longer allowed to authorize lower-friction reuse.
Frozen memory is not revoked history; it is a deliberate stop on future reuse.

### `revoked`

Use when remembered approval has been intentionally withdrawn and may no longer justify any later arrival shortcut.

### `unknown`

Use when missing receipts, clock uncertainty, or incomplete lineage prevent an honest freshness claim.
Unknown is not a softer `fresh`.
It is a proof problem.

## Cooling reasons

A row should never merely say `stale` or `cooling` without explanation.
At least one reason should be attached.

Suggested reasons:

- `no_recent_use`
- `never_reviewed_after_initial_approval`
- `linked_device_set_changed`
- `identity_epoch_changed`
- `role_or_scope_widened_since_last_review`
- `repeated_arrivals_ignored`
- `supporting_receipt_missing`
- `clock_uncertain`
- `constellation_policy_narrowed`

The product may compute more than one reason, but the strongest one should appear first.

## Fixed inspection order

Every approval-memory freshness surface should preserve the same sections in the same order:

1. **Remembered approval and granted scope**
2. **Freshness evidence**
3. **What this memory may still do now**
4. **Touch-renewal and narrowing options**
5. **Freeze / require-fresh / revoke options**
6. **Receipts and proof links**

### 1) Remembered approval and granted scope

This section should show:

- which remembered approval is in view
- who or what it applies to
- the granted scope as last reviewed
- the seat and governed scope from which it may still influence later arrivals

The operator must be able to answer: **what standing trust memory are we even talking about?**

### 2) Freshness evidence

This section should show:

- freshness class
- last explicit review time
- last actual use time
- primary cooling reasons
- whether the row is live or receipt-reconciled

The operator must be able to answer: **why does the product think this memory is fresh, cooling, stale, or frozen?**

### 3) What this memory may still do now

This section should show:

- whether later arrivals may still enter `matched, no auto-admit`, `identity-only admit`, or `claim-suggested`
- whether any arrival shortcut is blocked pending touch renewal
- whether the memory may still match all linked devices, one reviewed seat, or a narrower subset only
- what the product promises it will not do even while this memory remains live

The operator must be able to answer: **what does this remembered trust still authorize today, and where does that stop?**

### 4) Touch-renewal and narrowing options

This section should show:

- `Touch-renew` if the operator only wants to keep the same scope alive after review
- `Narrow scope` if earlier convenience was broader than intended
- whether a narrower scope would still satisfy current later-arrival needs
- whether the outcome changes the next expected review time

The operator must be able to answer: **how do I keep this memory usable without pretending nothing has changed?**

### 5) Freeze / require-fresh / revoke options

This section should show:

- `Freeze reuse` when the operator wants to keep history but stop further automatic reuse
- `Require fresh approval next time` when the operator wants remembered trust to stop satisfying the next arrival shortcut
- `Revoke memory` when remembered trust should no longer count even as reusable evidence
- which of those outcomes leave current local claims, binds, or bytes untouched

The operator must be able to answer: **how do I stop or cool this memory without accidentally mutating current subjects?**

### 6) Receipts and proof links

This section should show:

- which receipt created the original memory
- which receipt last renewed, narrowed, froze, or revoked it
- whether a further arrival receipt is still separate and later
- what next review expectation remains, if any

The operator must be able to answer: **what later evidence will prove this trust memory was refreshed, narrowed, frozen, or revoked?**

## Touch-renewal rules

`Touch-renew` is intentionally narrow.
It is allowed to do only three things:

- prove that the operator reviewed this remembered approval again
- keep or narrow the granted scope
- move the next expected freshness checkpoint forward if policy allows it

It must **not** silently:

- claim a current arrival
- bind a path
- materialize bytes
- widen linked-device scope
- restore frozen memory to a broader scope than the original reviewed grant promised

## Interaction with matched arrivals

Freshness and arrival matching are adjacent but different surfaces.

A matched-arrival row may point to freshness, but it should not replace it.
Likewise, a freshness row may show recent arrival evidence, but it should not pretend to be a claim or bind review.

Examples:

- `Maya / photos-collab -> cooling / last used 214d ago / later arrivals require touch renewal`
- `Studio-NAS / backup-read -> frozen / history retained / no future match reuse`

## Batch rules

Freshness queues may support batching, but only by common truthful outcome.

### Acceptable labels

- `Touch-renew 3 warm memories`
- `Freeze 4 stale memories`
- `Require fresh approval next time for 2 cooling memories`

### Unacceptable labels

- `Trust again`
- `Approve all remembered`
- `Keep auto-connect working`

A batch bar may not promise a broader result than every selected row actually shares.

## Dense and mobile rules

A dense row or mobile card may compress wording, but it must still preserve three cues:

- what remembered approval is in view
- what freshness class applies now
- what the next honest action is

`Maya / photos-collab · cooling · Touch-renew` is acceptable compression.
`Approved before` is not.

## CLI contract

Minimal commands:

```text
anonsync approval memory freshness list --seat self --scope family-arrivals
anonsync approval memory freshness show apm_01J...
anonsync approval memory touch-renew prepare --memory apm_01J... --seat self --plan
anonsync approval memory narrow prepare --memory apm_01J... --scope seat:self/photos-only --plan
anonsync approval memory freeze apm_01J...
anonsync approval memory require-fresh-next-time apm_01J...
anonsync approval memory revoke apm_01J...
```

Rules:

- list output should always expose `memory`, `freshness class`, `last used`, `scope`, and `next honest action`
- `touch-renew prepare` must render the fixed inspection order above before apply
- `freeze` and `require-fresh-next-time` must each preserve current local subjects unless a separate later review explicitly changes them
- a receipt printed after apply must clearly say whether the outcome was `renewed`, `narrowed`, `frozen`, `fresh-next-time-required`, or `revoked`

## Example workbench row

```text
Maya / photos-collab   granted: Maya + linked devices / photos family   cooling   last used 214d ago   Touch-renew
```

Opening the row should show, in order:

- which prior approval is being discussed
- why it is only `cooling` rather than `fresh`
- that later matched arrivals will no longer reach `claim-suggested` without touch renewal once it becomes `stale`
- that `Touch-renew` keeps current subject state untouched
- that `Freeze reuse` keeps historical proof but stops future shortcut reuse

## Why this matters

A weaker product shape would leave remembered approval immortal until manual revocation, or else abruptly make a later arrival fail without telling the operator that trust memory had quietly gone stale.
This spec proves the archive wants a stricter contract:

- remembered trust should have visible freshness classes
- cooling and stale reasons should be explicit
- touch renewal should be a separate reviewed act
- freezing future reuse should preserve history without pretending that history is still active trust
