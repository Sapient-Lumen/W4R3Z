# Offer-artifact expiry, exhaustion, and trust-promotion interface spec

## Purpose

The archive already separates portable offer artifacts from local claims, remembered approval from subject-level reuse policy, and approval freshness from descendant capability.
One real gap still remained:

> after a claim succeeds through a one-time or expiring invitation, the operator still needs one explicit answer to whether that invitation created any durable remembered approval at all, at what scope, and with what later reuse boundary.

This document turns that question into one explicit interface contract.
It is the offer-lifetime companion to `52-capability-offer-and-claim-artifact-spec.md` and the trust-lifecycle companion to `97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md`, `106-approval-memory-freshness-cooling-and-touch-renewal-interface-spec.md`, and `111-approval-memory-reuse-policy-and-subject-override-precedence-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Sync Share Dialog (Desktop)` still says link security may set an expiry period and use-count limit, while `Sync functionality in detail` still says you only need to approve a person once because approval is retained with their identity for later sharing.
`Link structure and flow` also still describes approval as minting a certificate and ACL entry after the approval succeeds.

Taken together, those current docs imply a real operator question:

- the invitation artifact itself may be one-time or time-bounded
- the first successful approval may still mint longer-lived identity-backed trust
- a later share may therefore reuse remembered trust even though the original invitation artifact is long gone
- nothing in that artifact-lifetime story should silently answer whether later convenience is allowed, what scope it reaches, or whether the first invitation was supposed to stay single-subject in spirit

That is not a criticism of expiring links or of certificate-backed sharing.
It is a criticism of any surface that leaves the operator reconstructing whether a consumed one-time or expiring invitation merely admitted *this one subject* or also promoted the remote party into durable remembered approval for later subjects.
AnonSync should therefore expose one explicit **offer-artifact expiry, exhaustion, and trust-promotion contract** wherever portable invitation lifetime and later approval reuse might otherwise blur together.

## Core rule

Portable invitation lifetime and durable trust lifetime are separate public facts.

Offer expiry, redemption exhaustion, or revocation governs whether the artifact can be redeemed again.
It does **not** by itself answer whether a successful claim created durable remembered approval.
Likewise, remembered approval created after a successful claim does **not** retroactively keep the offer artifact alive.

The product is not fully inspectable until it can answer seven questions in one place:

1. which offer artifact originally carried the authority
2. what happened to that artifact now (`active`, `consumed`, `expired`, `exhausted`, `revoked`)
3. whether any successful claim promoted durable approval memory at all
4. if promotion happened, what scope it reached (`this subject only`, `reviewed seat only`, `family reuse candidate`, `explanation only`)
5. whether later convenience still depends on a stricter subject-level reuse policy anyway
6. what tempting but unsafe shortcut is being refused
7. which receipt later proves both the artifact outcome and the durable-trust outcome

If the operator still has to infer from `used once`, `expired link`, `approved before`, or later auto-connect behavior whether one old invitation created standing remembered trust, the surface is not explicit enough.

## Public objects

### Offer trust-promotion row

A compact read object describing what durable trust, if any, survived after one offer artifact was claimed or exhausted.

Suggested fields:

- `offer_trust_promotion_row_id`
- `offer_ref`
- `seat_ref`
- `subject_ref`
- `artifact_terminal_posture` (`active`, `consumed`, `expired`, `exhausted`, `revoked`, `unknown`)
- `claim_outcome` (`not-claimed`, `claim-rejected`, `claim-applied`, `claim-applied-pending-review`, `unknown`)
- `promotion_posture` (`none`, `pending-reviewed-promotion`, `subject-only`, `reviewed-seat-only`, `family-reuse-candidate`, `explanation-only`, `frozen`, `unknown`)
- `promotion_scope_basis` (`offer-policy`, `approval-review`, `subject-policy`, `mixed`, `unknown`)
- `later_reuse_posture` (`not-applicable`, `eligible-subject-only`, `eligible-after-seat-check`, `subject-policy-blocked`, `fresh-approval-next-time`, `unknown`)
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Offer trust-promotion explanation

A read object explaining what happened to durable trust after the offer artifact's own lifetime ended or was consumed.

Suggested fields:

- `offer_trust_promotion_explanation_id`
- `offer_ref`
- `subject_ref`
- `artifact_terminal_posture`
- `claim_outcome`
- `promotion_posture`
- `promotion_scope_basis`
- `later_reuse_posture`
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Offer trust-promotion review plan

A prepared review object for one attempt to keep an accepted offer artifact as `this subject only`, promote it into broader remembered approval, or explicitly freeze it at explanation-only.

Suggested fields:

- `offer_trust_promotion_plan_id`
- `offer_ref`
- `seat_ref`
- `subject_ref`
- `current_artifact_terminal_posture`
- `current_promotion_posture`
- `requested_outcome` (`keep-subject-only`, `promote-reviewed-seat-only`, `promote-family-reuse-candidate`, `freeze-explanation-only`, `require-fresh-next-time`, `revoke-promotion`)
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Offer trust-promotion receipt

A durable object proving what long-lived trust, if any, survived after one offer artifact was claimed, consumed, or expired.

Suggested fields:

- `offer_trust_promotion_receipt_id`
- `offer_ref`
- `subject_ref`
- `previous_artifact_terminal_posture`
- `previous_promotion_posture`
- `outcome`
- `reviewed_at`
- `resulting_promotion_posture`
- `resulting_later_reuse_posture`
- `proof_refs[]`

## Artifact terminal postures

### `active`

Use when the artifact may still be redeemed again under its current policy.

### `consumed`

Use when the artifact completed a claim path that intentionally consumes the artifact regardless of any broader trust outcome.

### `expired`

Use when time-based policy ended future redemption.

### `exhausted`

Use when redemption-budget policy ended future redemption.

### `revoked`

Use when the sender or authority holder explicitly ended future redemption.

### `unknown`

Use when the product cannot honestly determine current artifact lifetime state.

## Promotion postures

### `none`

Use when the offer artifact did not create durable remembered approval beyond the local subject result.

### `pending-reviewed-promotion`

Use when the claim succeeded but broader remembered approval is still waiting for a separate review outcome.

### `subject-only`

Use when the result intentionally stays attached to this one governed subject and must not authorize later unrelated subjects.

### `reviewed-seat-only`

Use when durable memory exists, but only for one separately reviewed descendant seat.

### `family-reuse-candidate`

Use when the reviewed outcome intentionally created remembered approval that may later be considered for broader reuse, subject to all later freshness, capability, and subject-policy checks.

### `explanation-only`

Use when historical approval facts remain visible for provenance but must not drive later convenience.

### `frozen`

Use when prior broader promotion existed but later review froze further reuse.

### `unknown`

Use when the product cannot yet make an honest trust-promotion claim.

## Fixed inspection order

Every offer-trust-promotion surface should preserve the same sections in the same order:

1. **Offer artifact and current redemption posture**
2. **Claim outcome and promotion candidate**
3. **Current durable-trust posture and later reuse posture**
4. **What definitely is not being claimed**
5. **Admissible reviewed outcomes**
6. **Receipts and proof links**

### 1) Offer artifact and current redemption posture

This section should show:

- which offer artifact is in view
- how it was delivered
- whether it is still active, consumed, expired, exhausted, or revoked
- next honest action

The operator must be able to answer: **what happened to the invitation itself?**

### 2) Claim outcome and promotion candidate

This section should show:

- whether the artifact was claimed successfully
- what governed subject it admitted
- whether the successful claim created any promotion candidate at all
- whether broader trust still needs separate review

The operator must be able to answer: **did this artifact merely admit this subject, or is broader remembered approval even being considered?**

### 3) Current durable-trust posture and later reuse posture

This section should show:

- current promotion posture
- promotion scope basis
- later reuse posture
- whether stricter subject-level reuse policy still blocks later convenience anyway

The operator must be able to answer: **what durable trust survived, at what scope, and does it actually matter for later reuse?**

### 4) What definitely is not being claimed

This section should show:

- that artifact expiry does not retroactively revoke already-applied local subject outcomes
- that artifact consumption does not automatically imply broader remembered approval
- that later remembered approval does not mean the original artifact remains redeemable
- that this review does not itself approve a new subject, bind a path, or materialize bytes

The operator must be able to answer: **which tempting shortcut is being refused?**

### 5) Admissible reviewed outcomes

This section should show only honest next outcomes from current state, including:

- `Keep this subject only`
- `Promote to reviewed seat only`
- `Promote to family reuse candidate`
- `Freeze at explanation only`
- `Require fresh approval next time`
- `Revoke durable promotion`

Outcomes that would skip required approval, widen trust without review, or treat artifact survival and trust survival as the same fact must not be offered.

### 6) Receipts and proof links

This section should show:

- the originating offer artifact receipt
- the claim receipt proving the first successful admission
- any approval-memory lineage or subject-policy receipts that later narrow or allow reuse
- the current offer-trust-promotion receipt

The operator must be able to answer: **which proof shows what survived the invitation, and which proof limited it later?**

## Row language rules

Good row labels:

- `offer consumed · claim applied · subject only · fresh approval next time · Keep this subject only`
- `offer expired · claim applied · family reuse candidate · eligible after seat check · Open trust review`
- `offer exhausted · claim applied · explanation only · not applicable · Show receipts`

Bad row labels:

- `Already trusted`
- `Invite used`
- `Known peer now`
- `One-time link became normal`

The row should tell the truth about both lifetimes: the portable artifact lifetime and the durable-trust lifetime.

## CLI shape

```text
anonsync offer promotion list --seat self --scope recent-claims
anonsync offer promotion show --offer off_01J... --subject incoming:photos-2026 --seat self
anonsync offer promotion prepare --offer off_01J... --subject incoming:photos-2026 --outcome keep-subject-only --plan
anonsync offer promotion apply otp_01J...
```

Semantics:

- `offer promotion show` must work even after the original portable artifact has expired or been deleted, as long as claim receipts and local provenance still exist
- `offer promotion prepare` must restate artifact terminal posture and claim outcome before it shows any durable-trust outcome choices
- `offer promotion apply` must never silently widen remembered approval beyond the explicitly reviewed promotion outcome

## Dense/mobile rule

Dense or mobile surfaces may compress prose, but they must still preserve one visible artifact-lifetime fact, one visible claim fact, one visible promotion posture, and one honest next action.
They must never collapse `one-time link used once` into `trusted forever` or `expired invitation` into `all trust revoked`.
