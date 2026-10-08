# Offer redemption ledger, consumption budget, and multi-redeemer trust-fanout interface spec

## Purpose

The archive already separates:

- portable offer artifacts from claims
- offer-artifact lifetime from durable trust promotion
- sender intent from actual redeemer identity

One real gap still remained:

> when one portable offer can be redeemed more than once, the operator still needs one explicit answer to which exact attempts consumed the budget, which redeemers succeeded or failed, how much budget remains, and what trust did or did not fan out from each redemption event.

This document turns that question into one explicit interface contract.
It is the multi-redemption companion to `112-offer-artifact-expiry-and-trust-promotion-boundary-interface-spec.md` and the ledger companion to `113-offer-recipient-intent-and-redeemer-identity-boundary-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Sync Share Dialog (Desktop)` says a peer who gets the link may connect automatically when approval is disabled, says previously approved peers may be granted access automatically under `Only new peers`, says `All peers` can still force fresh approval for every folder, and says a link may be used only `N` times, with each `N+1` attempt by whoever failing.
`Link structure and flow` then says the actual requester sends a public key, approval identifies that requester by user name and fingerprint, and successful approval generates certificate-backed access plus an ACL entry.

Taken together, those current docs imply a real operator question:

- one portable artifact can have a shared consumption budget
- several distinct redemption attempts may hit that same budget
- some redeemers may succeed automatically, some may require approval, some may be rejected, and some may fail only because budget is exhausted
- successful redemption may create durable trust for that actual redeemer
- none of that means the artifact itself has one single durable-trust meaning

That is not a criticism of multi-use links or approval reuse.
It is a criticism of any surface that leaves the operator reconstructing which exact redeemer consumed which click, why the budget ran out, or which later remembered approval came from which redemption event.
AnonSync should therefore expose one explicit **offer redemption ledger and multi-redeemer trust-fanout contract** wherever offer budgets, repeated redemptions, and later trust reuse might otherwise blur together.

## Core rule

Redemption budget is artifact-scoped.
Trust consequence is redemption-scoped.

An offer artifact may have one expiry and one shared redemption budget.
Each redemption attempt is its own public event.
Each successful redemption may or may not create durable trust for the actual redeemer.
The artifact budget never stands in for the trust story, and the trust story never stands in for the budget story.

The product is not fully inspectable until it can answer eight questions in one place:

1. which offer artifact is in scope
2. what the artifact's total and remaining redemption budget is
3. which attempts have already consumed or failed against that budget
4. who made each attempt and on what proof basis
5. which attempt outcomes were automatic, approval-backed, rejected, expired, or budget-denied
6. what durable trust, if any, each successful redemption created
7. what tempting but unsafe shortcut is being refused
8. which receipts later prove budget consumption, per-attempt outcome, and any per-redeemer trust fanout

If the operator still has to infer from `link valid for 3 uses`, approval history, and later remembered approval which identities actually consumed that budget and what trust survived from each, the surface is not explicit enough.

## Public objects

### Offer redemption ledger row

A compact read object describing one portable artifact's shared budget and the per-attempt trust outcomes already attached to it.

Suggested fields:

- `offer_redemption_ledger_row_id`
- `offer_ref`
- `seat_ref`
- `subject_ref`
- `artifact_budget_class` (`single-use`, `bounded-multi-use`, `unbounded-until-expiry`, `unbounded-no-expiry`, `unknown`)
- `redemption_limit_total` nullable
- `redemption_count_consumed`
- `redemption_count_remaining` nullable
- `artifact_terminal_posture` (`active`, `partially-consumed`, `consumed`, `expired`, `revoked`, `superseded`, `unknown`)
- `attempt_summary`
- `trust_fanout_summary`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Offer redemption attempt entry

A read object for one concrete attempt against the shared offer artifact.

Suggested fields:

- `offer_redemption_attempt_id`
- `offer_ref`
- `attempt_index`
- `actual_redeemer_ref`
- `actual_redeemer_proof_basis`
- `attempt_time`
- `attempt_outcome_class` (`auto-admitted`, `approved`, `approved-subject-only`, `approved-reviewed-seat-only`, `promoted-broader`, `rejected`, `expired-denied`, `budget-denied`, `duplicate-denied`, `revoked-denied`, `unknown`)
- `budget_effect` (`consumed-one`, `did-not-consume`, `unknown`)
- `resulting_trust_posture`
- `explanation_summary`
- `proof_refs[]`

### Offer redemption budget explanation

A read object explaining why the artifact is still active, partially consumed, exhausted, or no longer redeemable.

Suggested fields:

- `offer_redemption_budget_explanation_id`
- `offer_ref`
- `artifact_budget_class`
- `redemption_limit_total`
- `redemption_count_consumed`
- `redemption_count_remaining`
- `artifact_terminal_posture`
- `last_budget_consuming_attempt_ref`
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Trust-fanout review plan

A prepared review object for deciding what trust, if any, should survive from one successful redemption in a multi-redeemer artifact history.

Suggested fields:

- `offer_trust_fanout_plan_id`
- `offer_ref`
- `seat_ref`
- `subject_ref`
- `attempt_ref`
- `current_attempt_outcome_class`
- `current_resulting_trust_posture`
- `requested_outcome` (`keep-subject-only`, `bind-reviewed-seat-only`, `promote-broader`, `freeze-fanout`, `reissue-new-artifact`, `revoke-derived-trust`, `no-change`)
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Offer redemption ledger receipt

A durable object proving one artifact's budget state and the per-attempt trust outcomes that matter later.

Suggested fields:

- `offer_redemption_ledger_receipt_id`
- `offer_ref`
- `attempt_ref`
- `recorded_at`
- `artifact_terminal_posture`
- `redemption_limit_total`
- `redemption_count_consumed`
- `redemption_count_remaining`
- `attempt_outcome_class`
- `actual_redeemer_ref`
- `resulting_trust_posture`
- `proof_refs[]`

## Artifact budget classes

### `single-use`

Use when exactly one budget-consuming successful redemption is allowed.

### `bounded-multi-use`

Use when the artifact may be redeemed more than once but only up to a fixed limit.

### `unbounded-until-expiry`

Use when redemption count is not capped but the artifact has a real expiry boundary.

### `unbounded-no-expiry`

Use when the artifact has neither count limit nor time limit.
This class should be rare and should render with stronger caution language.

### `unknown`

Use when the product cannot honestly determine the budget model.

## Attempt-outcome classes

### `auto-admitted`

Use when the attempt succeeded without fresh approval because the governing policy genuinely allowed it.

### `approved`

Use when the attempt succeeded after fresh approval and no narrower trust boundary is currently claimed.

### `approved-subject-only`

Use when the attempt succeeded but trust was intentionally kept at the governed-subject boundary.

### `approved-reviewed-seat-only`

Use when the attempt succeeded and trust survived only for one reviewed seat.

### `promoted-broader`

Use when the attempt succeeded and broader remembered approval was explicitly reviewed and promoted.

### `rejected`

Use when the attempt reached review but was denied.

### `expired-denied`

Use when the attempt failed because the artifact expired before redemption.

### `budget-denied`

Use when the attempt failed because the shared redemption budget was exhausted.

### `duplicate-denied`

Use when the attempt failed because it was a replay or duplicate of an already-accounted redemption path.

### `revoked-denied`

Use when the attempt failed because the artifact or authority had already been revoked.

### `unknown`

Use when the product cannot honestly classify the attempt outcome.

## Fixed inspection order

Every offer-redemption-ledger surface should preserve the same sections in the same order:

1. **Artifact budget and current terminal posture**
2. **Redemption attempt ledger**
3. **Per-attempt trust fanout**
4. **What definitely is not being claimed**
5. **Admissible reviewed outcomes**
6. **Receipts and proof links**

### 1) Artifact budget and current terminal posture

This section should show:

- which artifact is in view
- total limit, consumed count, and remaining count
- whether the artifact is active, partially consumed, consumed, expired, revoked, or superseded
- next honest action

The operator must be able to answer: **is the artifact still redeemable, and if not, why not?**

### 2) Redemption attempt ledger

This section should show:

- each recorded attempt in order
- actual redeemer identity and proof basis
- whether the attempt consumed budget
- whether the attempt was automatic, approved, rejected, expired-denied, budget-denied, or otherwise blocked

The operator must be able to answer: **who hit this artifact, in what order, and which attempts actually spent the budget?**

### 3) Per-attempt trust fanout

This section should show:

- resulting trust posture for each successful attempt
- whether that attempt stayed subject only, seat only, broader, frozen, or explanation only
- whether later remembered approval traces back to that attempt

The operator must be able to answer: **which exact redemption event created which later trust?**

### 4) What definitely is not being claimed

This section should say what the product is carefully refusing to imply.

Typical lines include:

- `shared budget does not prove all successful redeemers were equally intended`
- `artifact exhaustion does not prove all later trust has been revoked`
- `one successful redemption does not explain every later remembered approval`
- `one later remembered approval does not imply the artifact still has remaining budget`
- `two successful redeemers do not collapse into one generic accepted audience`

### 5) Admissible reviewed outcomes

Typical reviewed outcomes include:

- keep one successful redemption `subject only`
- bind one successful redemption to one reviewed seat only
- promote one successful redemption broader with explicit review
- freeze further trust fanout while leaving historical receipts intact
- revoke derived trust from one earlier redemption
- reissue a new artifact rather than stretching an old partially consumed one

### 6) Receipts and proof links

This section should expose:

- the artifact creation receipt
- attempt receipts in order
- any approval or mismatch receipts tied to specific attempts
- any later trust-promotion or trust-freeze receipts tied to those same attempts

## Interface rules

### One artifact card must not flatten multiple redeemers into one vague audience

Bad:

- `Redeemed by 3 people`
- `Accepted audience established`

Good:

- `Use 2 of 3 consumed`
- `Maya-phone -> approved subject only`
- `Noah-laptop -> approved broader`
- `3rd attempt -> budget denied`

### Budget rows and trust rows must stay adjacent but distinct

Budget truth should answer `can this artifact still be redeemed?`
Trust truth should answer `what later authority survived from each redemption?`
They may be shown side by side, but they must never collapse into one generic `link status` sentence.

### Partial consumption is its own stable state

`partially-consumed` is not just `still active` with a hidden counter.
It should render as its own state whenever remaining budget exists but prior redemptions already matter.

### Reissue should be a first-class safe action

When an artifact has mixed history, the safe next action is often `Reissue new artifact` rather than keep stretching the same partially consumed budget across more redeemers.
That action should render prominently whenever the ledger already contains unexpected or mixed trust outcomes.

## CLI sketches

```text
anonsync offer redemption-ledger show --offer off_01Jmaya_photos
anonsync offer redemption-ledger attempts --offer off_01Jmaya_photos
anonsync offer trust-fanout prepare --offer off_01Jmaya_photos --attempt ora_02 --outcome keep-subject-only --plan
anonsync offer trust-fanout apply otfp_01Jmaya
```

## Acceptance criteria

This spec is satisfied only if:

- one artifact can show several attempts without pretending they share one trust meaning
- remaining budget is visible without opening raw history
- a failed `budget-denied` or `expired-denied` attempt is distinguishable from a reviewed `rejected` attempt
- later remembered approval can be traced back to one exact successful attempt rather than only to the artifact as a whole
- dense/mobile surfaces still preserve `budget remaining` versus `trust fanout` as separate facts
- the safest recovery action can be `reissue new artifact` rather than `keep using the old one`

## Relation to the rest of the archive

This document depends on:

- `52-capability-offer-and-claim-artifact-spec.md`
- `112-offer-artifact-expiry-and-trust-promotion-boundary-interface-spec.md`
- `113-offer-recipient-intent-and-redeemer-identity-boundary-interface-spec.md`

This document should shape:

- offer views and review panes in `38-operator-workbench-interface-spec.md`
- portable-offer CLI grammar in `30-interface-spec.md`
- offer-redemption resources in `31-daemon-api-spec.md`
- operator review rules in `39-interface-pattern-language.md`
- later roadmap work around invitation governance, trust reuse, and artifact reissue defaults
