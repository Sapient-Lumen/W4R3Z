# Approval-memory lineage and authorization-trace interface spec

## Purpose

The archive already separates first approval from later matches, explains later-arrival causality, previews standing-policy edits, preserves policy lineage, classifies drift, ages intentional exceptions, and now treats remembered approval as a freshness lifecycle.
One gap still remained:

> when later convenience is still influenced by remembered trust, the operator must be able to ask **which exact old approval act is being reused, from which seat, with what scope, and what later trust mutations changed that memory before or after this match?**

This document turns that question into one explicit interface contract.
It is the provenance companion to `97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md`, the freshness companion to `106-approval-memory-freshness-cooling-and-touch-renewal-interface-spec.md`, and the authorization-history companion to `101-effective-arrival-explanation-and-counterfactual-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Sync functionality in detail`, `Sync Private Identity & Linking My Devices`, `Folder Types and Management`, and `Comprehensive guide to syncing (Desktop-Desktop)` together still describe a system where:

- approval can be retained with a person's identity so later sharing may not need approval again
- approvals can be issued from any linked device where the folder is active
- a remote user can choose to auto-approve all linked devices for future sharing after approving one
- pending folders can automatically connect if that user approved you before
- approval time details such as name, IP address, fingerprint, and approval request receipt date are visible when reviewing a request

That is real convenience and some of the ingredients for later inspection.
What current docs still do **not** expose as one first-class surface is the later answer to:

- which original approval act created the remembered trust now matching this arrival
- which seat or linked-device horizon spoke when that approval happened
- whether the remembered trust was later renewed, narrowed, frozen, or revoked before the current arrival
- whether the current arrival matched under the original trust version or a later rewritten one
- which receipt chain later proves that story without operator reconstruction

AnonSync should not accept reconstructive trust folklore here.
Any remembered approval that can still lower friction later should therefore also expose one explicit **lineage and authorization-trace contract**.

## Core rule

Remembered trust must be attributable, not just fresh.

The product is not fully inspectable until it can answer seven questions in one place:

1. which approval-memory family is in view
2. which exact approval or renewal event originally created the currently relevant memory
3. which seat, identity epoch, and governed horizon spoke in that event
4. which later trust mutations narrowed, renewed, froze, or revoked that memory
5. which lineage node was effective when a specific later arrival, match, or auto-admit suggestion occurred
6. whether current trust lineage is now broader, narrower, frozen, or revoked relative to that historical moment
7. which receipts prove every step without requiring private memory or log archaeology

If the operator still has to compare old approval rows, later arrival history, and support notes to decide **which trust act actually authorized the convenience they are seeing now**, the surface is not explicit enough.

## Public objects

### Approval-memory trace row

A compact read object describing one remembered approval family together with its current effective lineage head.

Suggested fields:

- `approval_memory_trace_row_id`
- `approval_memory_ref`
- `governed_scope`
- `current_lineage_node_ref`
- `origin_receipt_ref`
- `origin_seat_ref`
- `current_freshness_class`
- `current_scope_summary`
- `last_mutation_summary`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Approval-memory lineage node

A durable read object representing one specific authorization event in remembered-trust history.

Suggested fields:

- `approval_memory_lineage_node_id`
- `approval_memory_ref`
- `predecessor_node_ref` nullable
- `event_kind` (`initial-approval`, `touch-renewal`, `scope-narrowed`, `scope-widened-reviewed`, `reuse-frozen`, `fresh-next-time-required`, `revoked`)
- `acting_seat_ref`
- `acting_identity_epoch_ref`
- `governed_horizon`
- `result_scope_summary`
- `result_freshness_class`
- `receipt_ref`
- `effective_from`

### Approval-memory lineage timeline

A read object summarizing the full reviewed mutation chain for one remembered-approval family.

Suggested fields:

- `approval_memory_lineage_timeline_id`
- `approval_memory_ref`
- `current_head_ref`
- `nodes[]`
- `generated_at`
- `generation_basis` (`live`, `receipt-reconciled`, `history-rebuilt`)

### Approval-memory authorization trace explanation

A read object answering which lineage node mattered for one specific later subject or match.

Suggested fields:

- `approval_memory_authorization_trace_explanation_id`
- `approval_memory_ref`
- `subject_ref`
- `matched_lineage_node_ref`
- `current_head_ref`
- `subject_event_at`
- `authorization_posture_at_match` (`active`, `narrowed`, `cooling`, `stale-but-allowed`, `frozen`, `revoked`, `unknown`)
- `difference_from_current_head`
- `counterfactual_under_current_head`
- `proof_refs[]`

## Fixed inspection order

Every approval-memory trace surface should preserve the same sections in the same order:

1. **Remembered approval family and current head**
2. **Origin approval act**
3. **Lineage mutations since origin**
4. **Which node authorized this later subject**
5. **How current trust differs now**
6. **Receipts and proof links**

### 1) Remembered approval family and current head

This section should show:

- which remembered approval family is in view
- current effective scope
- current freshness class
- current head node id
- next honest action

The operator must be able to answer: **what standing trust memory are we tracing, and what is its head now?**

### 2) Origin approval act

This section should show:

- the original approval receipt
- the seat that spoke
- the governed horizon promised then
- the identity fingerprint or epoch in force then
- the scope that was granted then

The operator must be able to answer: **where did this remembered trust actually come from?**

### 3) Lineage mutations since origin

This section should show:

- each later node in order
- what changed (`touch-renew`, `narrow`, `freeze`, `require fresh next time`, `revoke`)
- who spoke for that mutation
- whether the mutation changed freshness only, scope only, both, or neither
- whether any mutation superseded the node that once authorized a later match

The operator must be able to answer: **what later trust edits happened after the original approval?**

### 4) Which node authorized this later subject

This section should show:

- the later subject or arrival under inspection
- the exact lineage node that was effective at match time
- what that node allowed then
- what it still did **not** allow then
- whether the later subject matched because of original approval, a later renewal, or a narrower remembered scope

The operator must be able to answer: **which exact trust version made this later convenience possible?**

### 5) How current trust differs now

This section should show:

- whether the current head is broader, narrower, fresher, cooler, frozen, or revoked relative to the matched node
- whether the same later subject would still match under current trust
- whether the subject is historically explained but no longer admissible under current trust
- whether current trust changed after the subject appeared

The operator must be able to answer: **would the same thing still happen today, and if not, why not?**

### 6) Receipts and proof links

This section should show:

- the receipt that created the origin node
- the receipts for each lineage mutation
- the subject-side receipt that proves when the later arrival or match occurred
- any missing proof that forces `unknown` posture

The operator must be able to answer: **what exact evidence later proves this whole trust story?**

## Trace rules

### No overwrite rule

A later touch-renewal, narrowing, freeze, or revocation must create a new lineage node.
It must not silently rewrite the original remembered-trust node out of history.

### Seat visibility rule

Every lineage node that can influence later arrivals must preserve:

- acting seat
- governed horizon
- identity epoch or fingerprint posture
- resulting scope summary

`approved before` is never enough provenance on its own.

### Match attribution rule

Any later arrival or matched draft that cites remembered trust must be able to point to one explicit lineage node.
If the engine cannot prove the node, the attribution posture should become `unknown`, not a guessed success story.

### Counterfactual rule

A trace surface should always say whether the same subject would still be authorized under the current lineage head.
This prevents the operator from treating old convenience as current truth.

### Non-effect rule

Inspection of lineage must not itself:

- renew trust
- widen trust
- claim a subject
- bind a path
- materialize bytes

Trace is explanation, not mutation.

## Dense and mobile rules

A dense row or mobile card may compress wording, but it must still preserve four cues:

- approval-memory family
- current head posture
- most recent lineage mutation
- next honest action

`Maya / photos-collab · head narrowed 21d ago · cooling · Show trace` is acceptable compression.
`Approved before` is not.

## CLI contract

Minimal commands:

```text
anonsync approval memory trace list --seat self --scope family-arrivals
anonsync approval memory trace show --memory apm_01J... --subject incoming:photos-2026 --seat self
anonsync approval memory trace show --memory apm_01J... --lineage
anonsync approval memory trace show --memory apm_01J... --at 2026-03-01T12:00:00Z
```

Rules:

- `trace list` should always expose `memory`, `current head`, `current scope`, `last mutation`, and `next honest action`
- `trace show --subject ...` must render the fixed inspection order above before any suggested follow-on action
- `trace show --lineage` must keep the node order stable and visible; clients may collapse detail but may not reorder history by recency alone
- any printed trace receipt summary must clearly say whether the later subject matched under `origin`, `renewed`, `narrowed`, `frozen`, `revoked`, or `unknown` trust posture

## Example workbench row

```text
Maya / photos-collab   head: narrowed-to-home-nas/photos-only   cooling   last mutation 21d ago   Show trace
```

Opening the row for `Photos-2026` should show, in order:

- the remembered approval family and current head
- the origin approval from `laptop-ember` with granted scope `Maya + linked devices / Photos family`
- the later node that narrowed reuse to `home-nas / photos-only`
- the fact that `Photos-2026` matched under the pre-narrowing node 34 days ago
- the fact that the same subject would **not** match under today's narrowed head without fresh review
- the receipts proving origin approval, later narrowing, and the later arrival timing

## Why this matters

A weaker product shape would let remembered trust feel inspectable only while it is fresh, but still make the operator reconstruct **which exact approval act** is actually being reused later.
This spec proves the archive wants a stricter contract:

- remembered approval should have lineage, not just freshness
- later convenience should point to one attributable authorization node
- later trust mutations should supersede by adding history, not by overwriting it
- present explanation should include a counterfactual about whether the same subject would still be authorized now
