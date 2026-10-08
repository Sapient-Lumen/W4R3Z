# Shareable-artifact carryforward, delta ledger, and refresh-notice interface spec

## Purpose

The archive now already has:

- offer issuance and reissue grammar
- external escalation packets with frozen reviewed manifests
- shareable-artifact head registers
- outbound channel execution and delivery claim ceilings
- durable confirmation rules so transient UI never becomes the only truth

What still remained too easy to reconstruct by hand was a narrower but recurring question:

> if someone already has an older reviewed artifact from this family, what exact compact surface tells us whether that artifact still stands, what changed in the newer one, and whether a terse refresh note is honest or a full reopen is required?

The head register answers **which artifact is current now**.
The channel-execution surface answers **what movement or receipt was witnessed**.
Neither one yet answers **what changed since the last already-shared artifact** without making the operator reopen lineage, compare frozen members manually, or guess from version/hash drift.

This document defines one first-class **carryforward profile**, one **delta ledger**, and one **refresh notice** object so reused or superseded shareable artifacts stop depending on manual diff folklore.

## Core rule

Whenever a shareable-artifact family already has a prior disclosed or previously-current shareable head and a newer shareable head, candidate head, or withdrawal verdict now exists, the product must keep six truths separate:

1. which older artifact is the comparison basis
2. whether that older artifact still stands unchanged, can be refreshed in place, should be replaced, or must be reopened from first principles
3. which field families or evidence classes actually changed
4. which unchanged guarantees are still being carried forward explicitly
5. which compact visible refresh note is honest for the intended audience
6. which stronger follow-up object is required if terse carryforward is not enough

The product must not force operators or recipients to infer semantic change from hash drift, timestamp drift, or a newer head pointer alone.

## Why this needs its own spec

The archive now has the ingredients for retained, frozen, shareable artifacts.
But real operator continuity keeps hitting a separate seam:

- an offer is reissued with a shorter expiry but the same role and redeemer class
- an escalation packet gains one fresh route snapshot while the diagnostic question remains the same
- a continuity bundle is re-cut with a newer witness receipt but unchanged recovery posture
- a previous packet is no longer current because the audience, authority, or blocker basis changed too much for a terse refresh to be honest

Without one carryforward contract, the product tends to fail in two opposite ways:

- it over-compresses and says `updated` or `new version` without telling the operator whether the older artifact still semantically stands
- it under-compresses and makes the operator reopen lineage and full diffs for every small refresh

Cross-reading the companion datacubes sharpened the missing shape:
current heads, visible public surfaces, and refresh notices are different objects with different jobs.

## Public objects

### Shareable-artifact carryforward profile

A compact read object describing how one prior shareable artifact relates to the current shareable posture for the same family.

Suggested fields:

- `shareable_artifact_carryforward_profile_id`
- `artifact_family_ref`
- `comparison_basis_ref`
- `current_shareable_head_ref` nullable
- `current_operational_head_ref` nullable
- `audience_class`
- `carryforward_verdict` (`same-head-still-current`, `reuse-unchanged`, `refresh-in-place`, `replace-with-new-head`, `reopen-required`, `withdrawn`, `unknown`)
- `question_scope_summary`
- `unchanged_guarantee_summary`
- `delta_ledger_ref` nullable
- `refresh_notice_ref` nullable
- `recommended_followup_object_kind` (`none`, `refresh-notice`, `new-artifact`, `full-compare`, `new-review`, `withdrawal-note`, `unknown`)
- `generated_at`

### Shareable-artifact delta row

One compact row describing a changed or explicitly unchanged family-local field class.

Suggested fields:

- `shareable_artifact_delta_row_id`
- `carryforward_profile_ref`
- `field_family` (`audience`, `authority-scope`, `question-prompt`, `expiry-window`, `redeemer-class`, `included-artifacts`, `redaction-profile`, `evidence-window`, `orientation-summary`, `transport-note`, `other`)
- `delta_kind` (`unchanged`, `narrowed`, `widened`, `refreshed`, `replaced`, `removed`, `unknown`)
- `visible_to_recipient` (`yes`, `no`, `mixed`)
- `summary`
- `stronger_followup_needed` (`no`, `optional`, `yes`)

### Shareable-artifact delta ledger

A durable compact comparison object for one family at one moment.

Suggested fields:

- `shareable_artifact_delta_ledger_id`
- `artifact_family_ref`
- `comparison_basis_ref`
- `candidate_head_ref`
- `rows[]`
- `delta_summary`
- `reopen_boundary_summary`
- `generated_at`

### Artifact refresh notice

A reviewed, audience-safe visible wrapper summarizing what changed since the comparison basis without replacing the deeper lineage or delta surfaces.

Suggested fields:

- `artifact_refresh_notice_id`
- `artifact_family_ref`
- `comparison_basis_ref`
- `current_shareable_head_ref` nullable
- `audience_class`
- `notice_state` (`draft`, `reviewed`, `issued`, `superseded`, `withdrawn`, `blocked`)
- `notice_kind` (`unchanged-carryforward`, `refresh-in-place`, `replace-now`, `reopen-required`, `withdrawal`)
- `visible_summary`
- `unchanged_claims[]`
- `changed_claims[]`
- `forbidden_shortcuts[]`
- `recipient_action_hint` (`keep-using-current`, `use-new-head`, `request-full-compare`, `stop-using-prior`, `wait`, `unknown`)
- `issued_at` nullable

### Refresh-notice receipt

A durable record proving how the carryforward verdict or visible refresh note changed.

Suggested fields:

- `artifact_refresh_notice_receipt_id`
- `artifact_family_ref`
- `comparison_basis_ref`
- `result_notice_ref` nullable
- `transition` (`generate-ledger`, `issue-notice`, `supersede-notice`, `withdraw-notice`, `reopen-family`, `clear-ambiguity`)
- `recorded_at`
- `proof_refs[]`

## Carryforward verdicts

### `same-head-still-current`

The comparison basis is still the current shareable head.
No newer shareable artifact displaced it.
A refresh notice is usually unnecessary.

### `reuse-unchanged`

A newer moment of review or resend exists, but the earlier artifact still stands semantically unchanged for the same audience and question.
A compact unchanged-carryforward notice may be emitted.

### `refresh-in-place`

The family remains the same and a compact recipient-safe refresh note is honest, but at least one field family changed.
The delta ledger must say which ones.

### `replace-with-new-head`

A new shareable head now exists and should replace the older one for ordinary use.
A refresh notice may summarize the replacement, but the visible current answer is `use the new head`.

### `reopen-required`

The change is too fundamental for terse carryforward.
Recipients or operators must be routed to a fuller compare/review object instead of one compact refresh note.
Examples include changed authority scope, widened audience, contradictory evidence basis, or a materially different question prompt.

### `withdrawn`

The older artifact should no longer be used and no replacement head is currently being blessed for ordinary reuse.
A withdrawal notice may exist.

## Fixed inspection order

Every carryforward / refresh surface should preserve this order:

1. **Artifact family and comparison basis**
2. **Current carryforward verdict**
3. **Delta ledger: what changed and what explicitly did not**
4. **Visible refresh notice**
5. **Recipient action and stronger follow-up boundary**
6. **Receipts and lineage proofs**

### 1) Artifact family and comparison basis

This section should show:

- artifact family id
- comparison-basis artifact
- current shareable head if one exists
- intended audience class
- why this comparison is being opened now

The operator must be able to answer: **which older artifact are we comparing against, and for whom?**

### 2) Current carryforward verdict

This section should show one of the verdicts above and one short explanation.

The operator must be able to answer: **does the older artifact still stand, does it refresh, does it get replaced, or must this be reopened?**

### 3) Delta ledger: what changed and what explicitly did not

This section should show both changed and unchanged field families.
Examples:

- expiry window narrowed from 7 days to 24 hours
- authority scope unchanged
- recipient class unchanged
- evidence window refreshed to a newer capture slice
- orientation summary replaced for clarity

The operator must be able to answer: **what actually changed, and what is being explicitly carried forward unchanged?**

### 4) Visible refresh notice

This section should show the exact compact note that is honest to send or display to the intended audience.
Examples:

- `Same offer family, narrower expiry only; role and redeemer pin unchanged.`
- `Same incident packet family; prior question unchanged; added one fresh route snapshot and newer timeline slice.`
- `Do not rely on the prior packet; authority and audience basis changed enough that a full new review is required.`

The operator must be able to answer: **what compact visible summary is honest without opening the full diff?**

### 5) Recipient action and stronger follow-up boundary

This section should show:

- `Keep using prior artifact`
- `Use new head instead`
- `Send new head with refresh notice`
- `Open full compare`
- `Reopen review before any outward reuse`
- `Withdraw previous artifact`

The operator must be able to answer: **what should the recipient or sender do next, and when is the compact note not enough?**

### 6) Receipts and lineage proofs

This section should show:

- head-change receipts
- freeze receipts
- prior disclosure or outbound execution refs where relevant
- refresh-notice receipts
- missing proof that forces `unknown` or `reopen-required`

The operator must be able to answer: **what later evidence proves this carryforward story?**

## Public rules

### Rule 1 — version/hash drift is not itself a semantic refresh notice

A different hash, timestamp, or revision marker may prove non-identity.
It does not by itself explain what changed or whether terse carryforward is honest.

### Rule 2 — unchanged carryforward should be explicit, not guessed

If the older artifact still stands semantically, the product should say so directly rather than forcing the operator to infer that nothing important changed.

### Rule 3 — refresh notices are audience-safe wrappers, not replacements for deep comparison

A visible refresh notice may summarize change.
It must not replace the fuller delta ledger or lineage surfaces for cases that demand deeper inspection.

### Rule 4 — reopen-required must block false compression

If scope, audience, governing question, or proof basis changed too much, the product should emit `reopen-required` instead of squeezing the change into one misleading sentence.

### Rule 5 — prior disclosure and current carryforward are related but different truths

The product may know that the prior artifact was copied, sent, or receipt-imported.
That still does not answer whether the old artifact remains current or what visible notice now applies.

## Dense row contract

A dense row should preserve these labels in this order:

- `Family`
- `Compared to`
- `Verdict`
- `Changed`
- `Unchanged`
- `Notice`
- `Next action`

## CLI contract

Minimal commands:

```text
anonsync artifact carryforward show --family artfam_01J... --compared-to art_01J...
anonsync artifact delta show --family artfam_01J... --compared-to art_01J...
anonsync artifact refresh-notice issue --family artfam_01J... --compared-to art_01J... --plan
anonsync artifact refresh-notice show arn_01J...
```

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following without reopening full lineage prose or diffing whole artifacts manually:

- whether the older artifact still semantically stands
- whether the family only refreshed in place or now requires replacement
- which field families changed
- which unchanged guarantees are being explicitly carried forward
- what short visible note is honest for the intended audience
- when terse carryforward is forbidden and a fuller compare/review must reopen

## Companions

- `140-external-escalation-packet-and-redaction-review-interface-spec.md`
- `161-offer-issuance-reissue-and-audit-surface-interface-spec.md`
- `247-shareable-artifact-lineage-head-register-and-warning-surface-interface-spec.md`
- `252-outbound-channel-execution-delivery-witness-and-claim-ceiling-interface-spec.md`
- `257-shareable-artifact-disclosure-queue-issued-head-and-current-surface-interface-spec.md`
