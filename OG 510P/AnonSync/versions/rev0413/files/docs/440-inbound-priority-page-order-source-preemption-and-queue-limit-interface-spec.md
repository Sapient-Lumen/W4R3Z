# Inbound priority page: order source, preemption, and queue-limit interface spec

## Purpose

The archive already had generic queue concepts.
What it still lacked was one exact page for the operator question:

> why is this inbound artifact not going first, where did the current priority rule come from, and which exceptions are overruling the obvious order?

Current official Resilio docs make this seam concrete.
They now expose per-share and global download priority, sticky local override behavior, preemption, internal exceptions, 50k active-queue ceilings, non-splittable-transfer exceptions, and visible-vs-actual order mismatch.
That is useful.
It should not remain a support-page footnote.

## Core decision

AnonSync must expose one first-class **Inbound priority** page whenever inbound execution order can be shaped by policy, inheritance, or queue exceptions.

The page exists to answer five things in one place:

1. which order policy is active
2. where the policy came from
3. whether this subject still inherits future defaults
4. what exception prevents the expected file from going first
5. whether the visible order is authoritative or cosmetic

## Fixed page order

1. **Priority verdict**
2. **Effective policy**
3. **Inheritance and override provenance**
4. **Active queue and exceptions**
5. **Visible-vs-actual order proof**
6. **Action matrix**
7. **Receipts**

### 1) Priority verdict

Show:

- `inbound_priority_page_id`
- subject in scope
- current `priority_verdict` (`natural-order`, `inherited-priority`, `local-override`, `queue-limited`, `exception-active`, `visible-order-mismatch`, `unknown`)
- strongest honest summary
- last evaluated time

### 2) Effective policy

Show:

- current basis (`none`, `mtime-newest-first`, `mtime-oldest-first`, `size-largest-first`, `size-smallest-first`, future typed bases)
- source (`line-default`, `global-default`, `subject-override`, `temporary-review`)
- whether the subject still inherits future global changes
- whether reverting the displayed value would restore inheritance or only clear the explicit local value

### 3) Inheritance and override provenance

Show:

- when the current policy was first frozen
- which action froze it
- which higher-level policy it no longer tracks
- how to return to inheritance deliberately

The operator must be able to answer:

> is this queue policy living on because I chose it once, or because the current global default still governs it?

### 4) Active queue and exceptions

List active or near-active rows with:

- artifact ref
- actual execution rank
- expected rank under pure policy
- exception class (`queue-window-full`, `non-splittable-transfer`, `internal-preemption-exception`, `error-rebuild`, `hold`) 
- whether a higher-priority arrival can suspend it

### 5) Visible-vs-actual order proof

If any browse list differs from actual execution order, show:

- authoritative ordering source
- surfaces still showing cosmetic order
- whether the mismatch is harmless or decision-relevant
- nearest honest page or pane to use instead

### 6) Action matrix

Possible actions include:

- `Keep natural order`
- `Adopt inherited priority`
- `Freeze subject override`
- `Return subject to inheritance`
- `Temporarily expedite selection`
- `Open transfer bottleneck review`

Each row must show:

- scope touched
- whether execution changes immediately
- whether inheritance is broken or restored
- performance / fairness tradeoff
- expected receipt

### 7) Receipts

Store durable receipts for:

- priority policy changes
- inheritance breakage
- inheritance restoration
- queue rebuilds caused by policy or file-state change
- operator expedites

## Public object

Fields:

- `inbound_priority_page_id`
- `subject_ref`
- `priority_verdict`
- `effective_policy`
- `provenance_rows[]`
- `queue_rows[]`
- `order_proof`
- `action_rows[]`
- `receipt_rows[]`
- `generated_at`

## Non-goals

This page does **not** replace transport-route explanation or download-availability proof.
It proves only **what inbound order policy currently applies, whether it is inherited or frozen, which exception is in charge, and which ordering surface is authoritative**.
