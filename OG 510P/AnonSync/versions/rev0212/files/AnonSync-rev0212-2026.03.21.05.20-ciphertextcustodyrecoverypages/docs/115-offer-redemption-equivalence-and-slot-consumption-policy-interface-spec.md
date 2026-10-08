# Offer redemption equivalence, repeat-redeemer collapse, and slot-consumption policy interface spec

## Purpose

The archive already separates:

- portable offer artifacts from claims
- offer-artifact lifetime from durable trust promotion
- sender intent from actual redeemer identity
- shared artifact budget from per-attempt trust fanout

One real gap still remained:

> after several attempts hit one portable artifact, the operator still needs one explicit answer to which attempts are genuinely *equivalent* to an already-accounted redemption, which attempts deserve a fresh slot, and which attempts should be refused until a new artifact is issued.

This document turns that question into one explicit interface contract.
It is the accounting-policy companion to `114-offer-redemption-ledger-and-multi-redeemer-trust-fanout-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Sync Share Dialog (Desktop)` says a link may be used only `N` times, with each `N+1` attempt by whoever failing; says `Only new peers` may reuse prior approval automatically; and says `All peers` can still force a fresh approval when connecting to another shared folder.
`Link structure and flow` and the desktop syncing guide still say the actual requester sends a public key, the approver reviews the requester identity/fingerprint, and successful approval mints certificate-backed access plus an ACL entry.

Taken together, those current docs imply a real operator question that still needs one cleaner contract:

- one artifact may have a flat shared click/use budget
- some attempts may come from the exact same redeemer or reviewed seat as an earlier attempt
- some attempts may come from a different descendant inside a remembered-trust family
- some attempts may be an already-approved redeemer hitting a *different* governed subject
- some attempts may be obvious retries or transport replays rather than genuinely new admissions
- a product that only says `use 2 of 3 consumed` still leaves too much room to reconstruct whether that meant two different redeemers, one repeated redeemer, or one replay that should have collapsed

That is not a criticism of use-count controls or approval reuse.
It is a criticism of any surface that leaves slot accounting too flat once identity, family, and subject equivalence all matter.
AnonSync should therefore expose one explicit **redemption equivalence and slot-consumption policy contract** wherever a portable offer's remaining budget might otherwise be stretched, replayed, or misread.

## Core rule

Redemption attempts are not automatically unique just because they hit the same artifact at different times.

The product must treat three facts as separate public facts:

1. the artifact's raw remaining budget
2. the equivalence class of the current attempt relative to prior attempts
3. the reviewed policy that decides whether this class collapses into an old slot, consumes a new slot, or requires a new artifact

The product is not fully inspectable until it can answer eight questions in one place:

1. which artifact and governed subject are in scope
2. which earlier attempt the current attempt is being compared against
3. whether the current attempt is replay-equivalent, reviewed-seat-equivalent, family-equivalent, subject-new-but-identity-known, or genuinely distinct
4. which budget-accounting policy currently governs this artifact
5. whether the current attempt would consume a fresh slot, collapse into an earlier slot, or be blocked pending reissue
6. what trust, if any, may survive even if the slot collapses
7. what tempting but unsafe shortcut is being refused
8. which receipts later prove the equivalence judgment and resulting slot treatment

If the operator still has to infer from raw attempt order, prior approval, and use-count settings whether a repeated redeemer should consume another slot, the surface is not explicit enough.

## Public objects

### Offer redemption equivalence row

A compact read object describing the current attempt, the nearest prior comparable attempt, and the budget-accounting result.

Suggested fields:

- `offer_redemption_equivalence_row_id`
- `offer_ref`
- `subject_ref`
- `current_attempt_ref`
- `comparison_attempt_ref` nullable
- `equivalence_class` (`replay-equivalent`, `same-reviewed-seat`, `same-reviewed-family`, `same-human-hint-only`, `same-known-peer-new-subject`, `distinct-reviewed-seat`, `unexpected-distinct-redeemer`, `unknown`)
- `budget_accounting_policy` (`collapse-transport-replay`, `collapse-reviewed-seat-repeat`, `consume-per-reviewed-seat`, `consume-per-successful-subject-admission`, `consume-every-successful-redemption`, `require-new-artifact-after-first-success`, `unknown`)
- `slot_effect` (`collapse-into-existing-slot`, `consume-new-slot`, `no-slot-change-failed-attempt`, `blocked-pending-reissue`, `unknown`)
- `resulting_trust_posture`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Redemption equivalence explanation

A read object explaining why the current attempt did or did not count as a fresh slot.

Suggested fields:

- `offer_redemption_equivalence_explanation_id`
- `offer_ref`
- `subject_ref`
- `current_attempt_ref`
- `comparison_attempt_ref`
- `equivalence_class`
- `budget_accounting_policy`
- `slot_effect`
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Slot-accounting review plan

A prepared review object for deciding whether one equivalence class should collapse, consume, or force reissue.

Suggested fields:

- `offer_slot_accounting_plan_id`
- `offer_ref`
- `subject_ref`
- `current_attempt_ref`
- `comparison_attempt_ref`
- `current_equivalence_class`
- `current_budget_accounting_policy`
- `requested_outcome` (`collapse-into-earlier-slot`, `consume-new-slot`, `require-new-artifact`, `freeze-at-subject-only`, `deny-as-duplicate-replay`, `keep-current-policy`)
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Slot-accounting receipt

A durable object proving how one attempt was classified relative to an earlier attempt and how that affected budget accounting.

Suggested fields:

- `offer_slot_accounting_receipt_id`
- `offer_ref`
- `subject_ref`
- `current_attempt_ref`
- `comparison_attempt_ref`
- `equivalence_class`
- `budget_accounting_policy`
- `outcome`
- `slot_effect`
- `resulting_trust_posture`
- `reviewed_at`
- `proof_refs[]`

## Equivalence classes

### `replay-equivalent`

Use when the current attempt is best understood as a transport/browser/client replay of an already-accounted redemption path rather than a new redeemer or new governed-subject admission.

### `same-reviewed-seat`

Use when the current attempt comes from the same reviewed seat as an earlier successful attempt.

### `same-reviewed-family`

Use when the current attempt comes from a different descendant but one already accepted reviewed family/constellation equivalence policy still governs both attempts.

### `same-human-hint-only`

Use when the product can only weakly say that the human label appears the same, but the evidence does not rise to reviewed-seat certainty.

### `same-known-peer-new-subject`

Use when the current attempt is from a redeemer already known or approved, but this governed subject is new enough that the accounting decision still matters explicitly.

### `distinct-reviewed-seat`

Use when the current attempt is from a meaningfully different reviewed seat and should not be collapsed by vague familiarity alone.

### `unexpected-distinct-redeemer`

Use when the current attempt differs from earlier expected or accepted redeemers and should be treated as genuinely distinct unless explicitly reviewed otherwise.

### `unknown`

Use when the product cannot honestly determine equivalence class.

## Budget-accounting policies

### `collapse-transport-replay`

Use when obvious transport/browser retries should never burn extra budget.

### `collapse-reviewed-seat-repeat`

Use when repeated attempts by the same reviewed seat should collapse into one previously-accounted slot.

### `consume-per-reviewed-seat`

Use when each distinct reviewed seat should count separately even if the family or human label overlaps.

### `consume-per-successful-subject-admission`

Use when the same redeemer may consume another slot for a genuinely different governed subject, but not for pure replay of the same subject.

### `consume-every-successful-redemption`

Use when every successful redemption counts, even if the redeemer was already known.
This class should be rendered with stronger caution because it is easy to misunderstand.

### `require-new-artifact-after-first-success`

Use when policy intentionally disallows stretching the same artifact across later equivalent or distinct redeemers once one success already happened.

### `unknown`

Use when the product cannot honestly determine the governing accounting rule.

## Fixed inspection order

Every redemption-equivalence surface should preserve the same sections in the same order:

1. **Artifact budget and current attempt**
2. **Nearest comparable earlier attempt**
3. **Equivalence class and accounting policy**
4. **What definitely is not being claimed**
5. **Admissible reviewed outcomes**
6. **Receipts and proof links**

### 1) Artifact budget and current attempt

This section should show:

- which offer artifact is in view
- what its remaining budget is right now
- which governed subject the current attempt targets
- what the current next honest action is

The operator must be able to answer: **what budget is at stake, for which subject, right now?**

### 2) Nearest comparable earlier attempt

This section should show:

- which earlier attempt the product believes is the closest meaningful comparison
- who made that earlier attempt
- what trust and slot effect followed then
- whether the comparison is strong, weak, or absent

The operator must be able to answer: **what prior event is this current attempt being compared against?**

### 3) Equivalence class and accounting policy

This section should show:

- the current equivalence class
- the governing accounting policy
- whether the attempt will collapse, consume, or be blocked pending reissue
- what trust can or cannot survive from that outcome

The operator must be able to answer: **why does this attempt count — or not count — as a new slot?**

### 4) What definitely is not being claimed

This section should make non-effects explicit.
Examples:

- `same human label` does not prove same reviewed seat
- `already approved before` does not automatically collapse this into an earlier slot
- `slot collapsed` does not silently widen remembered approval
- `consume new slot` does not prove the redeemer was unexpected or suspicious
- `require new artifact` does not revoke prior successful admissions

### 5) Admissible reviewed outcomes

The surface should only offer outcomes that preserve accounting honesty:

- `Collapse into earlier slot`
- `Consume new slot`
- `Require new artifact`
- `Freeze at subject only`
- `Deny as duplicate replay`
- `Keep current policy`

The UI must not flatten these into one generic `Accept` button.

### 6) Receipts and proof links

This section should link separately to:

- the parent offer artifact receipt
- the current attempt receipt
- the comparison attempt receipt when present
- the slot-accounting receipt
- any resulting trust-boundary receipt

## Interface consequences

### Dense rows

Dense rows should show, at minimum:

- `Budget`
- `Compare to`
- `Equivalence`
- `Slot effect`
- `Next action`

Good compression:

- `1/2 uses consumed   Compare: tablet-lapis #1   Same reviewed seat   Collapse into slot 1`

Bad compression:

- `Link reused`
- `Already approved`
- `Second click ignored`

### Review panes

Full review panes should prefer `Require new artifact` over vague continuity when equivalence is weak, trust is broad, or remaining budget is low.

### CLI/API symmetry

Text surfaces must expose the same contract as rich surfaces.
A CLI user must be able to ask not only `what happened?` but `why did this not count as a fresh slot?`

## Non-clone conclusion

Resilio's current docs still teach a useful lesson and a limit at the same time.
Use-count links, prior approval reuse, and approval review are all real conveniences worth learning from.
What AnonSync should not clone is a flat `used N times by whoever` story once the operator actually needs to know whether the next attempt is a replay, the same reviewed seat, the same family on a new subject, or a genuinely distinct redeemer.

AnonSync should therefore keep portable artifacts and bounded-use convenience while replacing the accounting folklore with one explicit equivalence-and-slot-treatment surface.
