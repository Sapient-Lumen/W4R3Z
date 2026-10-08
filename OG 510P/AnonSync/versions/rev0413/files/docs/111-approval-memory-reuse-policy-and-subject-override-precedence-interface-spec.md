# Approval-memory reuse policy and subject-override precedence interface spec

## Purpose

The archive already separates first approval from later matches, freshness, lineage, authorization trace, family rebase, descendant liveness, and descendant capability.
One gap still remained:

> after the product can show that remembered approval exists and that one descendant is eligible to act, the operator still needs one truthful answer to **whether this governed subject actually permits reuse of that old approval memory at all, or instead requires fresh approval here despite the remembered trust**.

This document turns that question into one explicit interface contract.
It is the subject-policy companion to `97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md`, the approval-seat companion to `96-approval-seat-and-constellation-scope-review-interface-spec.md`, and the precedence companion to `110-approval-memory-descendant-role-eligibility-and-capability-proof-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Folder Types and Management`, `Sync functionality in detail`, `Sync Private Identity & Linking My Devices`, `User Management`, and `Sync Share Dialog (Desktop)` together still describe a system where:

- a later pending folder can automatically connect if that user approved you before and one of their devices is online
- approval can be retained with a person's identity for later sharing
- linked devices can broaden who counts as approved in future sharing
- the share dialog can also be configured so **only new peers** may reuse old approval while already-approved peers connect automatically
- or more strictly so **all peers** still require a new approval when connecting to another shared folder
- a subject can therefore have remembered approval history and a live eligible descendant while still being governed by a fresh-approval override for this one subject

That is not a criticism of peer-to-peer reality or of cautious sharing options.
It is a criticism of any surface that leaves the operator reconstructing precedence from old approvals, linked-device memory, folder arrival state, and share-dialog settings scattered across different pages.
AnonSync should therefore expose one explicit **approval-memory reuse-policy and subject-override precedence contract** wherever remembered trust might otherwise imply too much.

## Core rule

Standing approval memory is not an unconditional entitlement to skip fresh approval.

The product is not fully inspectable until it can answer seven questions in one place:

1. which governed subject or incoming offer is being discussed
2. which remembered approval family would ordinarily match
3. what the subject-level reuse policy is for this exact subject
4. which rule wins when standing memory and subject policy disagree
5. whether current reuse is authorized now, authorized only after narrower checks, or blocked pending fresh approval
6. what tempting but unsafe shortcut is being refused
7. which receipt later proves that precedence outcome

If the operator still has to infer from `approved before`, `all peers`, `only new peers`, linked ownership, or pending-folder auto-connect whether this exact subject may reuse old trust now, the surface is not explicit enough.

## Public objects

### Approval-memory reuse policy row

A compact read object describing whether one governed subject may reuse remembered approval.

Suggested fields:

- `approval_memory_reuse_policy_row_id`
- `approval_memory_ref` nullable
- `seat_ref`
- `subject_ref`
- `subject_kind` (`incoming-share`, `share-link`, `approval-request`, `matched-arrival`, `local-reshare`, `unknown`)
- `standing_reuse_candidate` (`none`, `memory-match`, `memory-match-with-descendant`, `lineage-only`, `unknown`)
- `subject_reuse_policy` (`standing-reuse-allowed`, `reuse-known-peers-only`, `fresh-approval-all-peers`, `fresh-approval-new-seat`, `no-standing-reuse`, `unknown`)
- `precedence_outcome` (`reuse-authorized-now`, `reuse-authorized-after-seat-check`, `fresh-approval-required`, `blocked-by-subject-policy`, `explanation-only`, `unknown`)
- `winning_rule_basis` (`subject-policy`, `standing-memory`, `narrowing-policy`, `mixed`, `unknown`)
- `blocking_reason` nullable
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Approval-memory reuse policy explanation

A read object explaining why one governed subject did or did not inherit remembered approval convenience.

Suggested fields:

- `approval_memory_reuse_policy_explanation_id`
- `approval_memory_ref` nullable
- `subject_ref`
- `standing_reuse_candidate`
- `subject_reuse_policy`
- `precedence_outcome`
- `winning_rule_basis`
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Approval-memory reuse policy review plan

A prepared review object for one attempt to keep, narrow, or override remembered approval reuse for one governed subject without silently widening trust.

Suggested fields:

- `approval_memory_reuse_policy_plan_id`
- `approval_memory_ref` nullable
- `seat_ref`
- `subject_ref`
- `current_subject_reuse_policy`
- `current_precedence_outcome`
- `requested_outcome` (`allow-reuse-for-this-subject`, `require-fresh-approval`, `narrow-to-reviewed-seat`, `keep-explanation-only`, `remove-standing-match`, `dismiss-false-reuse`)
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Approval-memory reuse policy receipt

A durable object proving the result of one reviewed precedence decision.

Suggested fields:

- `approval_memory_reuse_policy_receipt_id`
- `approval_memory_ref` nullable
- `subject_ref`
- `previous_subject_reuse_policy`
- `previous_precedence_outcome`
- `outcome`
- `reviewed_at`
- `resulting_subject_reuse_policy`
- `resulting_precedence_outcome`
- `proof_refs[]`

## Standing reuse candidates

### `none`

Use when no remembered approval family currently matches the governed subject.

### `memory-match`

Use when remembered approval appears to match the subject at a family/policy level, but no particular descendant-seat reuse claim is being made yet.

### `memory-match-with-descendant`

Use when remembered approval appears to match and at least one descendant-seat reuse path is being evaluated separately.

### `lineage-only`

Use when old approval history matters for explanation but should not count as current reuse.

### `unknown`

Use when the product cannot honestly explain whether any standing match exists.

## Subject reuse policies

### `standing-reuse-allowed`

Use when this subject explicitly allows remembered approval reuse under the current policy boundary.

### `reuse-known-peers-only`

Use when this subject allows reuse only for already-reviewed peers or seats that still satisfy the standing match.

### `fresh-approval-all-peers`

Use when this subject requires a new approval even for previously approved peers.

### `fresh-approval-new-seat`

Use when remembered approval may survive at the family level, but this new seat or descendant still requires a fresh approval act.

### `no-standing-reuse`

Use when this subject intentionally forbids standing approval reuse at all.

### `unknown`

Use when the subject-level policy cannot be honestly determined.

## Precedence outcomes

### `reuse-authorized-now`

Use when standing approval memory may be reused for this subject now under the winning rule.

### `reuse-authorized-after-seat-check`

Use when subject policy allows reuse in principle, but one narrower seat/descendant review still has to succeed.

### `fresh-approval-required`

Use when this subject requires a new approval act despite the remembered-trust match.

### `blocked-by-subject-policy`

Use when subject policy or narrowing forbids reuse even though remembered approval lineage still exists.

### `explanation-only`

Use when old approval history remains visible for explanation but must not drive current convenience.

### `unknown`

Use when the product cannot yet make an honest precedence claim.

## Fixed inspection order

Every reuse-policy surface should preserve the same sections in the same order:

1. **Governed subject and standing match candidate**
2. **Subject reuse policy and current precedence outcome**
3. **Winning rule and blocker details**
4. **What definitely is not being claimed**
5. **Admissible reviewed outcomes**
6. **Receipts and proof links**

### 1) Governed subject and standing match candidate

This section should show:

- which governed subject or incoming offer is in view
- whether any remembered approval family currently matches
- whether any descendant-seat reuse path is separately in play
- next honest action

The operator must be able to answer: **what subject is at stake, and is remembered trust even being considered here?**

### 2) Subject reuse policy and current precedence outcome

This section should show:

- subject reuse policy
- current precedence outcome
- whether remembered approval may be reused now, only after narrower checks, or not at all
- whether the subject is intentionally stricter than the standing memory

The operator must be able to answer: **does this subject let old approval memory count, or does it require fresh approval anyway?**

### 3) Winning rule and blocker details

This section should show:

- winning rule basis
- blocking reason if present
- whether the deciding factor came from subject policy, standing memory, narrowing policy, or mixed reasoning
- whether a separate descendant-capability review still remains open

The operator must be able to answer: **why did this rule win, and what exactly still blocks lower-friction approval?**

### 4) What definitely is not being claimed

This section should show:

- that remembered approval lineage does not override a stricter subject-level fresh-approval rule
- that descendant eligibility does not itself authorize reuse when the subject policy demands a new approval
- that this review does not itself approve the subject, widen future trust, claim a path, or materialize bytes
- that `reuse-known-peers-only` is not the same as `reuse every seat automatically`

The operator must be able to answer: **what unsafe convenience inference is the product refusing to make for me?**

### 5) Admissible reviewed outcomes

This section should keep distinct outcomes such as:

- `Allow reuse for this subject`
- `Require fresh approval`
- `Narrow to reviewed seat`
- `Keep explanation only`
- `Remove standing match`
- `Dismiss false reuse`

These must remain distinct because they preserve different amounts of present convenience, future reuse, and historical explanation.

### 6) Receipts and proof links

This section should show:

- the standing approval lineage/trace node that would otherwise match
- the subject policy source or offer/security record that set the override
- any descendant-capability receipt the precedence answer depends on
- the reviewed reuse-policy receipt that proves the winning rule and outcome

The operator must be able to answer: **what later evidence proves why this subject did or did not inherit remembered approval convenience?**

## Surface grammar

### Dense rows

Dense rows should keep five items adjacent:

1. governed subject
2. standing reuse candidate
3. subject reuse policy
4. precedence outcome
5. next honest action

Example:

```text
incoming:photos-2026   memory match with descendant   fresh approval all peers   fresh approval required   Open approval review
```

### Review verbs

Preferred verbs:

- `Show reuse policy`
- `Require fresh approval`
- `Allow reuse for this subject`
- `Narrow to reviewed seat`
- `Keep explanation only`

Avoid:

- `Already approved here`
- `Auto connect trusted peer`
- `Known device can skip review`
- `Approved before so continue`
- `Use remembered approval`

## Relationship to other specs

- `97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md` answers **how old approval memory may match a later arrival at all**
- `106-approval-memory-freshness-cooling-and-touch-renewal-interface-spec.md` answers **whether that memory is still fresh enough to reuse in general**
- `107-approval-memory-lineage-and-authorization-trace-interface-spec.md` answers **which old approval act or later trust mutation created the memory**
- `110-approval-memory-descendant-role-eligibility-and-capability-proof-interface-spec.md` answers **whether a particular descendant may act for this subject if reuse is allowed in principle**
- this document answers **whether this exact governed subject even permits remembered approval reuse in the first place, and which rule wins when subject policy is stricter**

## Design consequences

### Consequence 1: subject policy can be stricter than standing trust

Remembered approval may still exist, remain fresh, and still be traceable, yet the current governed subject may intentionally require a new approval anyway.
The interface must make that override first-class.

### Consequence 2: precedence must be inspectable before action

The product should show the winning rule before the operator reaches the actual approval action, not only after a failed shortcut.

### Consequence 3: descendant capability is necessary but not sufficient

A descendant may be eligible to act, but still not authorized to skip fresh approval for this subject.
The product must keep capability and reuse-policy precedence separate.

### Consequence 4: review cannot secretly do the approval

Inspecting or tightening reuse-policy precedence must not itself approve the subject, widen future approval memory, claim a path, or materialize bytes.
Those later acts still need their own reviewed receipts.
