# Offer preview sufficiency, omission classes, and omitted-governance non-inference spec

## Purpose

The archive already separates:

- delivery preview from authoritative local intake
- canonical artifact identity from carrier aliases
- preview-visible hints from sealed authority-bearing fields
- sender intent from actual redeemer identity
- artifact budget from later trust fanout

One real gap still remained:

> once a minimal preview shows a human-recognition label or approximate size, the operator still needs one explicit answer to whether that preview is sufficient for any meaningful decision, and which missing governance facts must remain visibly absent instead of being silently inferred.

This document turns that boundary into one explicit interface contract.
It is the decision-sufficiency companion to `117-offer-delivery-handoff-provenance-and-preview-authority-boundary-interface-spec.md`, the omission-truth companion to `119-offer-preview-hint-provenance-and-sealed-authority-field-partition-spec.md`, and the portable-offer intake companion to `52-capability-offer-and-claim-artifact-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful but incomplete way.
`Link structure and flow` says the landing page shows only basic info about the folder you are about to receive, specifically folder name and size.
The same article shows that the full link carries more than that, including folder id, temporary key, expiry time, and the producer version.
Meanwhile `Sync Share Dialog (Desktop)` shows that the actual sharing surface also involves permission level, approval policy (`Only new peers` versus `All peers`), expiration period, and use-count limits.

That is helpful product design, but it still leaves one operator question too reconstructive:

- the preview may be enough to recognize the thing a human expected
- the preview may be enough to notice a glaring mismatch in label or approximate size
- the preview is not enough to infer permission type, approval posture, expiry policy, use-count budget, or later trust-promotion defaults
- if those omissions are not made explicit, users will still backfill them from memory, habit, or wishful thinking

That is not a criticism of small previews.
It is a criticism of any surface that lets `I saw the right label and size` stand in for `I know the governance story of this offer`.
AnonSync should therefore expose one explicit **preview sufficiency and omission non-inference contract** wherever a portable offer is previewed before full local parse and later review.

## Core rule

A preview may be useful without being decision-sufficient.

The product must treat six facts as separate public facts:

1. which decisions the preview is sufficient for right now
2. which decisions are still blocked even though a preview exists
3. which governance-bearing fields are omitted from the preview entirely
4. which omitted fields will become available only after local parse
5. which later decisions still require claim or approval review even after local parse
6. which receipt later proves that the product refused to infer the missing parts

The product is not fully inspectable until it can answer ten questions in one place:

1. what the preview actually showed
2. what the preview omitted
3. whether the preview is sufficient for human recognition
4. whether it is sufficient for local routing or placement suggestion
5. whether it is sufficient for permission/governance judgment
6. whether it is sufficient for trust/admission judgment
7. which exact omitted fields block those later judgments
8. what tempting but unsafe inference is being refused
9. what the next honest action is
10. which receipt later proves the omission-aware decision path

If the operator still has to infer from `label looks right` and `size seems familiar` whether the offer is read-only, requires fresh approval, is near expiry, has one use left, or will mint broad remembered trust, the surface is not explicit enough.

## Public objects

### Offer preview-sufficiency row

A compact read object describing what one preview is sufficient for, what it still omits, and what next action remains honest.

Suggested fields:

- `offer_preview_sufficiency_row_id`
- `offer_ref` nullable
- `delivery_event_ref`
- `preview_surface`
- `preview_fields[]`
- `omitted_governance_fields[]`
- `recognition_sufficiency` (`none`, `weak-recognition`, `recognition-sufficient`, `unknown`)
- `routing_sufficiency` (`none`, `placement-hint-only`, `routing-sufficient`, `unknown`)
- `governance_sufficiency` (`insufficient`, `partial-but-non-decisive`, `locally-parsed-needed`, `review-needed`, `unknown`)
- `trust_sufficiency` (`insufficient`, `approval-review-needed`, `claim-review-needed`, `receipt-backed`, `unknown`)
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Offer omission explanation

A read object explaining which missing fields matter and why the preview cannot support stronger claims yet.

Suggested fields:

- `offer_preview_omission_explanation_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `preview_summary`
- `omitted_governance_fields[]`
- `recognition_sufficiency`
- `routing_sufficiency`
- `governance_sufficiency`
- `trust_sufficiency`
- `unsafe_inferences_refused[]`
- `why`
- `proof_refs[]`

### Offer preview-sufficiency review plan

A prepared review object for deciding whether to continue to local parse, request a narrower delivery method, or stop at recognition only.

Suggested fields:

- `offer_preview_sufficiency_plan_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `requested_outcome` (`continue-to-local-parse`, `show-routing-only`, `freeze-at-recognition-only`, `reissue-narrower-offer`, `require-fresh-approval-later`, `keep-current-policy`)
- `current_recognition_sufficiency`
- `current_governance_sufficiency`
- `current_trust_sufficiency`
- `blocking_omissions[]`
- `effect_summary`
- `non_effect_summary`
- `receipt_promise`

### Offer preview-sufficiency receipt

A durable object proving that one preview was treated with the correct decision scope and non-inference boundaries.

Suggested fields:

- `offer_preview_sufficiency_receipt_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `preview_surface`
- `preview_fields[]`
- `omitted_governance_fields[]`
- `recognition_sufficiency`
- `routing_sufficiency`
- `governance_sufficiency`
- `trust_sufficiency`
- `unsafe_inferences_refused[]`
- `outcome`
- `recorded_at`
- `proof_refs[]`

## Sufficiency classes

### Recognition sufficiency

#### `weak-recognition`

Use when the preview offers only a partial or low-confidence human cue.
Examples include a familiar-looking label without corroborating context.

#### `recognition-sufficient`

Use when the preview is good enough for a human to say `this appears to be the subject I expected`, while still refusing governance or trust conclusions.

### Routing sufficiency

#### `placement-hint-only`

Use when the preview can safely inform a tentative local placement suggestion or inbox grouping, but not a durable bind.

#### `routing-sufficient`

Use rarely, only when a local-only intake path has enough explicit context to choose a staging location without pretending that claim or governance review is complete.

### Governance sufficiency

#### `insufficient`

Use when the preview omits important policy-bearing fields such as permission class, approval posture, expiry, use-count, scope narrowing, or trust-promotion posture.

#### `partial-but-non-decisive`

Use when some governance hints are present but the preview still cannot justify a durable action.

#### `locally-parsed-needed`

Use when the next truthful step is local parse because the governing facts exist in the artifact but are not yet available to the operator.

#### `review-needed`

Use when the artifact has already been parsed locally, but a later approval or claim review still governs the real next action.

### Trust sufficiency

#### `approval-review-needed`

Use when durable admission or remembered-trust consequence still depends on a later approval review.

#### `claim-review-needed`

Use when the local product can parse the offer but still cannot honestly say the offer is accepted, claimed, or trusted.

#### `receipt-backed`

Use only after the later review chain has finished and the receipt set proves the outcome.

## Omitted governance fields

Surfaces should render omitted governance-bearing fields explicitly when relevant.
Suggested omissions include:

- `permission-class-omitted`
- `approval-policy-omitted`
- `expiry-policy-omitted`
- `use-count-policy-omitted`
- `trust-promotion-policy-omitted`
- `carrier-successor-relation-omitted`
- `recipient-intent-strength-omitted`
- `role-eligibility-omitted`

The point is not to flood the UI with field names.
The point is to prevent a preview from looking complete just because its omissions stayed invisible.

## Fixed inspection order

Every preview-sufficiency surface should preserve the same sections in the same order:

1. **What the preview showed**
2. **What the preview omitted**
3. **What this is sufficient for right now**
4. **What this is not sufficient for yet**
5. **Unsafe inferences refused**
6. **Next honest action**
7. **Receipts and proof links**

## Dense-row contract

Dense rows should keep five adjacent chips or phrases:

- `Preview`
- `Missing`
- `Enough for`
- `Not enough for`
- `Next action`

Allowed compression:

- `Preview: label, size`
- `Missing: permissions, expiry`
- `Enough for: recognition`
- `Not enough for: approval`
- `Next: inspect locally`

Forbidden compression:

- `Looks right`
- `Safe to connect`
- `Known share`
- `Ready`

## Review outcomes

Admissible reviewed outcomes include:

- `continue to local parse`
- `keep at recognition only`
- `allow routing hint only`
- `require narrower redelivery`
- `escalate to approval review`
- `freeze ambiguous preview`

The important part is that the product must never let `recognition sufficient` collapse into `governance sufficient`.

## CLI parity

CLI and textual surfaces should expose the same sufficiency truth without relying on color or card layout.

Illustrative commands:

```text
anonsync offer preview-sufficiency list --state active-intake
anonsync offer preview-sufficiency show --delivery dev_01J...
anonsync offer preview-sufficiency explain --delivery dev_01J...
anonsync offer preview-sufficiency prepare --delivery dev_01J... --outcome continue-to-local-parse --plan
anonsync offer preview-sufficiency apply opsp_01J...
```

Textual output should preserve at least:

- preview fields shown
- omitted governance fields
- sufficiency by decision domain
- unsafe inferences refused
- next honest action

## Non-goals

This document does not:

- replace carrier-alias normalization
- replace field-partition truth
- decide final approval policy or claim outcome
- require every preview to expose every omitted field verbatim on one line

It only requires the product to make preview usefulness and preview insufficiency explicit enough that operators stop filling governance gaps from memory.

## Acceptance test

The interface is good enough when a cautious operator can say all of the following without guesswork:

- `The preview is enough for me to recognize the subject.`
- `The preview is not enough for me to know permissions, approval policy, expiry, or use budget.`
- `The product named those omissions instead of hiding them.`
- `The next action is to inspect locally, not to assume the governance story.`
- `If I later approve or claim this subject, I can prove that those later decisions did not rely on preview familiarity alone.`
