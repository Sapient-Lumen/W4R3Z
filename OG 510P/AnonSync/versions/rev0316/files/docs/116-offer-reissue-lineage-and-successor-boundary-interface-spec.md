# Offer reissue lineage, successor-artifact boundary, and budget-reset interface spec

## Purpose

The archive already separates:

- offer-artifact lifetime from durable trust promotion
- sender intent from actual redeemer identity
- artifact-level budget from per-attempt trust fanout
- repeated-attempt equivalence from honest slot treatment

One real gap still remained:

> once the honest next action becomes `reissue new artifact`, the operator still needs one explicit answer to whether the replacement artifact is a true fresh invitation, a narrow successor for the same governed subject, or a risky continuation that is carrying forward too much from the old artifact.

This document turns that boundary into one explicit interface contract.
It is the successor-lineage companion to `112-offer-artifact-expiry-and-trust-promotion-boundary-interface-spec.md`, `114-offer-redemption-ledger-and-multi-redeemer-trust-fanout-interface-spec.md`, and `115-offer-redemption-equivalence-and-slot-consumption-policy-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful but incomplete way.
`Sync Share Dialog (Desktop)` says a link may expire after `N` days, may be used only `N` times by whoever, and that after expiry new peers need a **new link from the folder owner**.
At the same time, `Sync functionality in detail` still says that by default you only need to approve a person once because Sync retains a certificate with their identity, while an optional setting can still require approval every time for another shared folder.
`Link structure and flow` still says successful approval mints certificate-backed access for the actual requester.

Taken together, those current docs imply a real operator question that still needs one cleaner contract:

- the old artifact may be expired, exhausted, or intentionally frozen
- the product may honestly recommend `reissue new artifact`
- the new artifact may target the same governed subject, a narrower subject, or a broader future audience
- some trust memory from the old artifact or old redeemer may still exist elsewhere
- without one lineage surface, the operator still has to reconstruct whether the new artifact is a fresh budget island or an accidental continuation of old assumptions

That is not a criticism of reissuing links.
It is a criticism of any surface that says only `get a new link from the folder owner` while leaving predecessor relation, carried-forward policy, and budget reset to folklore.
AnonSync should therefore expose one explicit **offer reissue lineage and successor-boundary contract** wherever a replacement artifact is created after expiry, exhaustion, mismatch, or explicit policy tightening.

## Core rule

A replacement artifact is not just another encoding of the old artifact unless the surface proves that it is.

The product must treat five facts as separate public facts:

1. why the predecessor artifact can no longer be used for this next admission story
2. whether the successor artifact is semantically identical, narrowed, broadened, or freshly scoped
3. which predecessor facts are intentionally carried forward
4. which predecessor facts definitely do **not** carry forward
5. which receipt later proves the exact predecessor-to-successor relation

The product is not fully inspectable until it can answer nine questions in one place:

1. which predecessor artifact is being replaced
2. which governed subject or subject set is in scope
3. why reissue was chosen instead of reusing the old artifact
4. whether the successor is same-scope, narrowed, broadened, or freshly scoped
5. whether the successor budget is a full reset, inherited cap, or intentionally zero until review completes
6. whether sender intent, redeemer expectations, approval requirements, or trust-promotion defaults changed
7. what durable trust from earlier redemptions still exists independently of the successor artifact
8. what tempting but unsafe continuity shortcut is being refused
9. which receipts later prove the predecessor/successor boundary

If the operator still has to infer from an old `expired` badge, remembered approval, and a new copied link whether the replacement artifact really reset the invitation story, the surface is not explicit enough.

## Public objects

### Offer reissue-lineage row

A compact read object describing one predecessor artifact, one successor artifact, and the reviewed relation between them.

Suggested fields:

- `offer_reissue_lineage_row_id`
- `predecessor_offer_ref`
- `successor_offer_ref`
- `subject_ref`
- `reissue_reason` (`expired`, `budget-exhausted`, `equivalence-too-weak`, `unexpected-redeemer`, `policy-tightened`, `operator-rotated`, `delivery-only-copy`, `unknown`)
- `successor_relation` (`same-scope-successor`, `narrowed-successor`, `broadened-successor`, `fresh-scope-successor`, `delivery-only-encoding`, `unknown`)
- `budget_reset_posture` (`fresh-budget-island`, `same-budget-family`, `carried-cap-with-review`, `no-budget-until-review`, `unknown`)
- `carried_forward_policy_summary`
- `explicit_non_carry_summary`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Offer reissue-boundary explanation

A read object explaining why the successor is or is not a clean replacement boundary.

Suggested fields:

- `offer_reissue_boundary_explanation_id`
- `predecessor_offer_ref`
- `successor_offer_ref`
- `subject_ref`
- `reissue_reason`
- `successor_relation`
- `budget_reset_posture`
- `carried_forward_policy_summary`
- `non_effect_summary`
- `why`
- `proof_refs[]`

### Offer reissue review plan

A prepared review object for deciding whether a successor artifact should inherit, narrow, freeze, or freshly reset predecessor assumptions.

Suggested fields:

- `offer_reissue_plan_id`
- `predecessor_offer_ref`
- `successor_offer_ref` nullable
- `subject_ref`
- `requested_outcome` (`issue-fresh-successor`, `issue-narrowed-successor`, `issue-broadened-successor`, `re-encode-only`, `freeze-old-and-stop`, `reissue-after-fresh-approval`, `keep-current-policy`)
- `proposed_budget_reset_posture`
- `proposed_carry_forward_summary`
- `explicit_non_carry_summary`
- `effect_summary`
- `blockers[]`
- `receipt_promise`

### Offer successor-boundary receipt

A durable object proving how one successor artifact relates to one predecessor artifact.

Suggested fields:

- `offer_successor_boundary_receipt_id`
- `predecessor_offer_ref`
- `successor_offer_ref`
- `subject_ref`
- `reissue_reason`
- `successor_relation`
- `budget_reset_posture`
- `carried_forward_policy_summary`
- `explicit_non_carry_summary`
- `outcome`
- `reviewed_at`
- `proof_refs[]`

## Reissue reasons

### `expired`

Use when the predecessor artifact naturally aged out and a later admission needs a successor artifact.

### `budget-exhausted`

Use when the predecessor artifact has no remaining shared redemption budget.

### `equivalence-too-weak`

Use when the current attempt could not honestly collapse into an earlier slot and the remaining artifact is no longer the right vessel.

### `unexpected-redeemer`

Use when sender intent and actual redeemer mismatch makes reissue safer than stretching the predecessor.

### `policy-tightened`

Use when approval, reuse, or scope policy became stricter and a fresh artifact boundary is part of the safety story.

### `operator-rotated`

Use when the operator intentionally rotates the artifact even though budget may technically remain.

### `delivery-only-copy`

Use only when the operator is changing encoding or transport wrapper without changing the artifact's semantic identity.
This class must be rare and rendered with stronger proof requirements.

## Successor relations

### `same-scope-successor`

Use when the successor governs the same subject and same authority class but intentionally starts a fresh artifact story.

### `narrowed-successor`

Use when the successor keeps part of the predecessor's purpose but reduces audience, role, scope, or reuse policy.

### `broadened-successor`

Use when the successor intentionally widens a predecessor boundary.
This class should require stronger review language.

### `fresh-scope-successor`

Use when the successor starts a new governed subject story and should not be rendered as mere continuation.

### `delivery-only-encoding`

Use when the artifact's semantic identity is unchanged and only its packaging changed.
This class must never silently reset budget or trust lineage.

## Budget reset postures

### `fresh-budget-island`

Use when the successor artifact starts a fully separate redemption budget and should not be confused with predecessor slot history.

### `same-budget-family`

Use when the successor intentionally remains inside one shared budget family.
This class should be rare and rendered with strong caution.

### `carried-cap-with-review`

Use when some predecessor budget constraint intentionally follows the successor, but only because explicit review said so.

### `no-budget-until-review`

Use when the successor object exists in draft or frozen form but cannot yet be redeemed.

## Fixed inspection order

Every reissue-lineage surface should preserve the same sections in the same order:

1. **Predecessor posture and why it stopped being the right artifact**
2. **Successor scope and relation to predecessor**
3. **Budget reset and carry-forward policy**
4. **What definitely is not being carried forward**
5. **Admissible reviewed outcomes**
6. **Receipts and proof links**

### 1) Predecessor posture and why it stopped being the right artifact

This section should show:

- predecessor artifact ID
- predecessor terminal or risky posture
- governed subject in scope
- reissue reason
- next honest action before any successor is assumed

### 2) Successor scope and relation to predecessor

This section should show:

- whether a successor already exists or is still a draft
- successor relation class
- whether sender intent, redeemer expectations, approval policy, or trust-promotion defaults changed
- whether the successor is merely a re-encoding or a genuinely new invitation boundary

### 3) Budget reset and carry-forward policy

This section should show:

- budget reset posture
- whether old slot history still matters for explanation only or for future budget accounting
- any explicit carried-forward constraints
- any explicit carried-forward trust that survives independently of the successor artifact

### 4) What definitely is not being carried forward

This section should make the strongest non-claims obvious.
Examples:

- `new link does not erase earlier successful redemption receipts`
- `fresh successor does not silently inherit old sender-intent match outcome`
- `same subject does not imply same budget family`
- `delivery-only copy does not reset expiry or use count`
- `remembered approval may still exist, but it is not evidence that this successor stayed narrow enough`

### 5) Admissible reviewed outcomes

Admissible outcomes should include:

- `Issue fresh successor`
- `Issue narrowed successor`
- `Issue successor after fresh approval`
- `Record delivery-only re-encoding`
- `Freeze predecessor and stop`
- `Require broader review before issue`

### 6) Receipts and proof links

This section should link separately to:

- predecessor artifact receipt
- predecessor redemption or accounting receipts that motivated reissue
- successor issue receipt or draft plan
- successor-boundary receipt proving what did and did not carry forward

## Surface rules

- `Reissue new artifact` must always open a predecessor/successor boundary review unless the action is provably `delivery-only-encoding`
- a successor artifact must never silently inherit predecessor budget exhaustion, mismatch acceptance, or sender-intent match outcome without explicit carry-forward language
- a `delivery-only-encoding` outcome must be rendered distinctly from `issue fresh successor`
- if a successor broadens audience, role, or reuse policy, the surface must say `broadened successor` plainly rather than calling it mere reissue
- dense/mobile surfaces may compress prose, but they must still keep predecessor posture, successor relation, budget reset posture, and next honest action adjacent

## Non-clone conclusion

Resilio's current docs still make `get a new link from the folder owner` a useful operational answer, but not yet a complete governance answer.
AnonSync should keep the convenience of easy reissue while refusing to let successor artifacts blur into predecessor history.
A replacement artifact must have one explicit lineage boundary so operators can tell whether they started a fresh invitation story, continued one under review, or accidentally carried forward more trust and budget than they meant to.
