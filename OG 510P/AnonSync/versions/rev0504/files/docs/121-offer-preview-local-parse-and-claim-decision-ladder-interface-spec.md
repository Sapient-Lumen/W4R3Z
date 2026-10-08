# Offer preview, local-parse, and claim decision-ladder interface spec

## Purpose

The archive already separates:

- delivery preview from authoritative local intake
- preview hints from sealed authority-bearing fields
- preview sufficiency from omitted governance truth
- offers from claims and claims from receipts

One practical gap still remained:

> even after those distinctions exist, the operator can still lose track of **which rung** they are on right now.

This document makes that rung explicit.
It is the bridge between `117-offer-delivery-handoff-provenance-and-preview-authority-boundary-interface-spec.md`, `119-offer-preview-hint-provenance-and-sealed-authority-field-partition-spec.md`, `120-offer-preview-sufficiency-and-omitted-governance-non-inference-spec.md`, and `66-claim-and-adoption-intake-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs are good enough to make the problem visible.
A link can open in a browser, show basic folder info, and hand off into the app.
The same share may also arrive by QR, copied text, or manual entry.
Those are useful mechanics.
But the operator still needs one explicit answer to four distinct questions:

- am I still at preview only?
- has the local app parsed the artifact yet?
- is the artifact now understood but still awaiting claim or approval review?
- did something durable actually happen already?

Without that ladder, people naturally compress the sequence into one story:
`I saw the right thing, opened it, and the app recognized it, so I am basically done.`

AnonSync must refuse that compression.

## Core rule

Preview, local parse, claim preparation, and apply are separate public rungs.
No surface may collapse them into one ambiguous success moment.

The product is not fully inspectable until it can answer seven questions in one place:

1. what rung the operator is on right now
2. what new facts became available at this rung
3. what stronger facts are still unavailable
4. what decision domains are now unlocked
5. what decision domains are still blocked
6. what the next honest action is
7. which receipt later proves the transition between rungs

## Public objects

### Offer decision-ladder row

A compact read object that states the operator's current rung and what it means.

Suggested fields:

- `offer_decision_ladder_row_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `claim_ref` nullable
- `current_rung`
- `previous_rung` nullable
- `preview_summary`
- `parsed_summary`
- `claim_summary`
- `enough_for[]`
- `not_enough_for[]`
- `missing_fields[]`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Offer decision-ladder explanation

A read object explaining why the current rung is the current rung.

Suggested fields:

- `offer_decision_ladder_explanation_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `claim_ref` nullable
- `current_rung`
- `rung_reason`
- `newly_available_facts[]`
- `still_blocked_facts[]`
- `unsafe_inferences_refused[]`
- `why`
- `proof_refs[]`

### Offer decision-ladder review plan

A prepared review object for moving from one rung to another without silently widening meaning.

Suggested fields:

- `offer_decision_ladder_plan_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `claim_ref` nullable
- `current_rung`
- `requested_rung`
- `requested_outcome` (`continue-to-local-parse`, `stay-at-recognition-only`, `allow-routing-hint-only`, `prepare-claim`, `require-approval-review`, `reject-ambiguous-offer`, `reissue-narrower`, `keep-current-state`)
- `blockers[]`
- `effect_summary`
- `non_effect_summary`
- `receipt_promise`

### Offer decision-ladder receipt

A durable object proving that one rung transition happened and what it did not imply.

Suggested fields:

- `offer_decision_ladder_receipt_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `claim_ref` nullable
- `rung_before`
- `rung_after`
- `newly_available_facts[]`
- `still_blocked_facts[]`
- `outcome`
- `recorded_at`
- `proof_refs[]`

## Ladder rungs

### `preview-only`

Use when the operator has only a transport or wrapper surface.
No local artifact parse has completed yet.

### `recognition-only`

Use when the preview is strong enough for the operator to say `this appears to be the thing I expected`, while governance and trust remain blocked.

### `routing-hint-only`

Use when the current information can help stage or group the arrival locally, but still does not justify claim or permission inference.

### `locally-parsed-unreviewed`

Use when the local app has parsed the artifact and can state its declared policy, but no claim or approval review has yet occurred.
This rung is extremely important because it often *feels* more final than it is.

### `claim-review-needed`

Use when the artifact is understood locally but the next truthful step is still a reviewed claim, approval, or admission choice.

### `claim-prepared`

Use when the operator has prepared a specific local outcome, but apply has not happened yet.
This is the plan-bearing rung.

### `applied`

Use only when the reviewed local outcome has actually been committed.
This rung must still preserve what earlier rungs did *not* prove.

### `frozen-ambiguous`

Use when the product intentionally refuses to continue because the preview or parse story is too ambiguous to compress safely.

### `superseded`

Use when a later reissue, successor artifact, or newer review displaced the current ladder.

## Fixed inspection order

Every decision-ladder surface should preserve the same sections in the same order:

1. **Current rung**
2. **What changed at this rung**
3. **What is still blocked**
4. **Enough for / not enough for**
5. **Next honest action**
6. **Receipts and proof links**

### 1) Current rung

This section should say the rung plainly.
Examples:

- `Current rung: recognition only`
- `Current rung: locally parsed, review still needed`
- `Current rung: claim prepared, not yet applied`

### 2) What changed at this rung

This section should state the newly available truth.
Examples:

- browser preview showed label and approximate size
- local parse revealed canonical artifact identity and declared policy fields
- claim preparation chose local path, role, and materialization mode

### 3) What is still blocked

This section should state what remains unavailable or unreviewed.
Examples:

- permissions still not accepted locally
- approval still not granted
- expiry and use-count parsed, but durable trust still not promoted

### 4) Enough for / not enough for

This section should keep decision scope adjacent.
The user should not have to merge this mentally from separate cards.

### 5) Next honest action

This section should expose one truthful next move.
Examples:

- `inspect locally`
- `prepare claim`
- `request narrower reissue`
- `stop at recognition only`
- `refresh because the offer drifted`

### 6) Receipts and proof links

This section should show which later receipt will prove the current rung transition.

## Action hierarchy rules

### Rule 1 — do not make the primary button outrun the rung

If the current rung is `recognition-only`, the primary action should not pretend the operator is already at `claim-prepared`.

### Rule 2 — local parse is a real transition, not cosmetic background work

If local parse completes, the surface must visibly advance the rung.
Do not silently replace preview hints with parsed truth while leaving the operator on the same-looking card.

### Rule 3 — claim prep is not apply

A prepared claim must remain visibly reversible and drift-checkable.
`Ready` is not enough language.

### Rule 4 — applied should preserve the earlier ladder story

Once applied, later audit should still be able to answer:

- what the preview showed
- what local parse added
- what the claim review chose
- what apply committed

## Dense-row contract

A dense row should preserve six adjacent phrases or chips:

- `Rung`
- `New`
- `Missing`
- `Enough for`
- `Not enough for`
- `Next`

Allowed compression:

- `Rung: parsed`
- `New: policy fields`
- `Missing: claim review`
- `Enough for: inspect`
- `Not enough for: accept`
- `Next: prepare claim`

Forbidden compression:

- `Opened`
- `Known`
- `Ready`
- `Safe`
- `Connected`

## CLI parity

Illustrative commands:

```text
anonsync offer ladder list --state active-intake
anonsync offer ladder show --delivery dev_01J...
anonsync offer ladder explain --delivery dev_01J...
anonsync offer ladder prepare --delivery dev_01J... --outcome prepare-claim --plan
anonsync offer ladder apply oldp_01J...
anonsync offer ladder receipt show oldr_01J...
```

Textual output must preserve:

- current rung
- newly available facts
- still blocked facts
- enough for / not enough for
- next honest action

## Acceptance test

The interface is good enough when a cautious operator can say all of the following without guesswork:

- `I know whether I am still looking at preview, or whether the app has actually parsed the artifact.`
- `I know what local parse changed.`
- `I know whether claim or approval review is still required.`
- `I know what the next honest action is.`
- `I can later prove which rung transition actually happened.`
