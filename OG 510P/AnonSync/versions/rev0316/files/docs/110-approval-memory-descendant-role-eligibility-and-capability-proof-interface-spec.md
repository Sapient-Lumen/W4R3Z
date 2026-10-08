# Approval-memory descendant role-eligibility and capability-proof interface spec

## Purpose

The archive already separates first approval from later matches, freshness, lineage, authorization trace, family rebase after constellation mutation, and descendant liveness.
One gap still remained:

> after trust family membership and descendant liveness are explained, the operator still needs one truthful answer to **which descendants may actually act as byte sources, approval seats, both, or neither for this governed subject right now, and on what proof**.

This document turns that question into one explicit interface contract.
It is the per-subject capability companion to `109-approval-memory-descendant-liveness-and-reachability-confidence-interface-spec.md`, the authority companion to `96-approval-seat-and-constellation-scope-review-interface-spec.md`, and the byte-truth companion to `91-fetchability-and-full-copy-witness-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Sync Private Identity & Linking My Devices`, `User Management`, `Folder Types and Management`, `Synchronization Modes`, and `Sync functionality in detail` together still describe a system where:

- you can approve a request from any linked device where the folder is active
- all devices linked to one identity act as Owners
- a later pending folder can auto-connect if that user approved you before and one of their devices is online
- selective-sync fetch still requires at least one online peer that actually has the files
- a descendant can therefore be linked, remembered, and even live without one first-class answer to whether it is actually eligible to serve bytes or approve this subject now

That is not a criticism of peer-to-peer reality or of convenience itself.
It is a criticism of any surface that lets `known device`, `linked owner`, or `online peer` masquerade as proof of current subject capability.
AnonSync should therefore expose one explicit **descendant role-eligibility and capability-proof contract** wherever remembered approval or linked-family convenience might otherwise imply too much.

## Core rule

Current liveness is not current role eligibility.

The product is not fully inspectable until it can answer seven questions in one place:

1. which governed subject is being discussed
2. which descendant seat/member/device is being discussed
3. which role is being evaluated (`byte-source`, `approval-seat`, `both`, or `explanation-only`)
4. whether that role is actually eligible now, eligible only after more proof, blocked, or explanation-only
5. what evidence or blocker produced that answer
6. what tempting but unsafe capability claim is being refused
7. which receipt later proves that posture

If the operator still has to infer from linked ownership, peer presence, remembered approval, or folder visibility whether a descendant may actually serve bytes or approve this subject now, the surface is not explicit enough.

## Public objects

### Approval-memory descendant capability row

A compact read object describing one descendant's current per-subject role eligibility.

Suggested fields:

- `approval_memory_descendant_capability_row_id`
- `approval_memory_ref`
- `seat_ref`
- `subject_ref`
- `descendant_ref`
- `descendant_kind` (`reviewed-seat`, `linked-member`, `hidden-member`, `reappeared-member`, `historical-node`, `unknown`)
- `liveness_class`
- `candidate_role` (`byte-source`, `approval-seat`, `both`, `explanation-only`, `unknown`)
- `eligibility_class` (`eligible-now`, `eligible-after-proof`, `blocked-no-bytes`, `blocked-no-active-share`, `blocked-fresh-approval-required`, `blocked-policy`, `explanation-only`, `unknown`)
- `proof_basis` (`live-byte-proof`, `live-share-membership`, `authority-proof`, `lineage-only`, `mixed`, `unknown`)
- `blocking_reason` nullable
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Descendant capability explanation

A read object explaining why one descendant currently carries a particular role-eligibility posture for one subject.

Suggested fields:

- `approval_memory_descendant_capability_explanation_id`
- `approval_memory_ref`
- `subject_ref`
- `descendant_ref`
- `candidate_role`
- `eligibility_class`
- `proof_basis`
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Descendant capability review plan

A prepared review object for one attempt to tighten or correct descendant capability claims without silently widening trust or materializing bytes.

Suggested fields:

- `approval_memory_descendant_capability_plan_id`
- `approval_memory_ref`
- `seat_ref`
- `subject_ref`
- `descendant_ref`
- `current_candidate_role`
- `current_eligibility_class`
- `requested_outcome` (`record-byte-source-proof`, `record-approval-seat-proof`, `mark-explanation-only`, `require-fresh-approval`, `freeze-subject-reuse`, `dismiss-false-capability`)
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Descendant capability receipt

A durable object proving the result of one reviewed descendant-capability decision.

Suggested fields:

- `approval_memory_descendant_capability_receipt_id`
- `approval_memory_ref`
- `subject_ref`
- `descendant_ref`
- `previous_candidate_role`
- `previous_eligibility_class`
- `outcome`
- `reviewed_at`
- `resulting_candidate_role`
- `resulting_eligibility_class`
- `proof_refs[]`

## Candidate roles

### `byte-source`

Use when the current question is whether this descendant may honestly count as a current source of bytes for the governed subject.

### `approval-seat`

Use when the current question is whether this descendant may honestly approve, renew, or extend authority for the governed subject.

### `both`

Use when the product is evaluating both operational roles together and can explain each one without collapsing their proofs.

### `explanation-only`

Use when the descendant remains important for lineage and explanation, but should not be treated as a current operational actor for this subject.

### `unknown`

Use when the product cannot honestly explain which role is even being claimed.

## Eligibility classes

### `eligible-now`

Use when the product has enough current proof to let the descendant count in the evaluated role now.

### `eligible-after-proof`

Use when the descendant may plausibly count in the role, but one material proof step is still missing.

### `blocked-no-bytes`

Use when the descendant may be live or linked, but the product cannot honestly count it as a current byte source for the subject.

### `blocked-no-active-share`

Use when the descendant may be live or linked, but the governed subject is not active there in the way the claimed role requires.

### `blocked-fresh-approval-required`

Use when remembered approval history is insufficient and a fresh approval act is required before the descendant may count in the evaluated role.

### `blocked-policy`

Use when current standing policy or reviewed narrowing forbids the role even if the descendant is live.

### `explanation-only`

Use when the descendant is intentionally retained for historical explanation and should not be treated as a current actor.

### `unknown`

Use when the product lacks enough evidence to make an honest eligibility claim.

## Fixed inspection order

Every descendant-capability surface should preserve the same sections in the same order:

1. **Governed subject and descendant identity**
2. **Candidate role and current eligibility**
3. **Proof basis and blockers**
4. **What definitely is not being claimed**
5. **Admissible reviewed outcomes**
6. **Receipts and proof links**

### 1) Governed subject and descendant identity

This section should show:

- which remembered-approval family is in view
- which governed subject is in view
- which descendant seat/member/device is being discussed
- next honest action

The operator must be able to answer: **what subject is at stake, and which descendant are we judging?**

### 2) Candidate role and current eligibility

This section should show:

- candidate role
- eligibility class
- liveness class carried forward from the liveness layer
- whether the role is current, conditional, blocked, or explanation-only

The operator must be able to answer: **what role is this descendant trying to fill for this subject, and is that actually allowed now?**

### 3) Proof basis and blockers

This section should show:

- proof basis
- last supporting proof age where relevant
- blocking reason if present
- whether the missing proof is about bytes, active-share posture, authority, or policy

The operator must be able to answer: **why did the engine reach this eligibility answer, and what exactly is still missing?**

### 4) What definitely is not being claimed

This section should show:

- that family membership alone does not prove byte-source capability
- that current liveness alone does not prove approval-seat capability
- that linked ownership alone does not prove this descendant may act for this subject right now
- that capability review does not itself renew trust freshness, widen scope, claim arrivals, bind paths, or materialize bytes

The operator must be able to answer: **what unsafe convenience inference is the product refusing to make for me?**

### 5) Admissible reviewed outcomes

This section should keep distinct outcomes such as:

- `Record byte-source proof`
- `Record approval-seat proof`
- `Freeze subject reuse`
- `Require fresh approval`
- `Mark explanation only`
- `Dismiss false capability`

These must remain distinct because they preserve different amounts of future convenience and historical explanation.

### 6) Receipts and proof links

This section should show:

- the remembered-approval lineage nodes that still matter
- the descendant-liveness receipts that this capability claim depends on
- the byte-source or approval-seat proof receipts that support `eligible-now`
- the reviewed capability receipt that proves the current outcome

The operator must be able to answer: **what later evidence proves that this descendant really was or was not eligible to act for this subject?**

## Surface grammar

### Dense rows

Dense rows should keep five items adjacent:

1. descendant identity
2. governed subject
3. candidate role
4. eligibility class
5. next honest action

Example:

```text
desktop-ash   incoming:photos-2026   approval-seat   eligible after proof   Require fresh approval
```

### Review verbs

Preferred verbs:

- `Show capability proof`
- `Record byte-source proof`
- `Record approval-seat proof`
- `Require fresh approval`
- `Freeze subject reuse`
- `Mark explanation only`

Avoid:

- `Known device can act`
- `Use this owner`
- `Approve here`
- `Source available`
- `Reconnect and use`

## Relationship to other specs

- `109-approval-memory-descendant-liveness-and-reachability-confidence-interface-spec.md` answers **how alive is this descendant?**
- this document answers **given that posture, may this descendant actually act for this subject now?**
- `96-approval-seat-and-constellation-scope-review-interface-spec.md` still governs approval seat choice and approval horizon when an approval action is actually taken
- `91-fetchability-and-full-copy-witness-spec.md` still governs truthful file/materialization claims

## Design consequences

### Consequence 1: eligibility must remain per subject

A descendant may be eligible to serve bytes for one subject and explanation-only for another.
The surface must stay keyed to one governed subject, not to generic device confidence.

### Consequence 2: byte-source and approval-seat proofs may diverge

The same descendant may be eligible as a byte source while blocked as an approval seat, or vice versa.
The surface must keep those roles explicit instead of flattening them into `available`.

### Consequence 3: linked ownership is evidence, not verdict

Linked ownership, remembered approval, and current liveness may all contribute to a capability answer, but none of them should silently become the answer.

### Consequence 4: capability review cannot secretly do the action

Reviewing or tightening capability posture must not itself fetch bytes, claim a subject, bind a path, or approve another peer.
Those later acts still need their own reviewed receipts.
