# Portable-offer composer and issuance-review interface spec

## Purpose

The archive now has strong recipient-side truth about:

- delivery provenance
- preview hints versus sealed authority fields
- preview sufficiency and omission truth
- preview/local-parse/claim ladders
- intake review before local bind or authority widening

What it still lacked was the sender-side companion.

> if the product is careful only after an offer arrives, but sloppy when the offer is composed, it will still recreate Resilio's strongest seam: the meaning lives in dialog ritual instead of one reviewed contract.

This document defines the composition and issuance surface for portable offers.

## Why this needs its own spec

Current Resilio docs are good enough to show both the strength and the gap.
The desktop share dialog exposes link versus QR, permission type, approval requirement, expiry, and click-count limits.
That is more serious than a toy `Share` button.
But the resulting semantics are still spread across:

- folder type
- key versus link versus QR
- approval options that differ by share mechanism
- read-only outcomes that may require manual read-only-key ritual
- single-file share behavior that has different expiry and redemption limits than ordinary folder sharing

The lesson is not `Resilio forgot about governance`.
The lesson is:

> governance still arrives as a pile of controls rather than one explicit issuance story saying who this is for, what the preview shows, what remains sealed until local parse, what role is being offered, what redemption budget applies, and what later receipt proves it.

AnonSync should therefore make issuance itself a reviewed act.

## Core rule

A portable offer must be composed through one issuance review, even when the product later renders it from a compact share button.

Every serious issuance surface must keep seven truths adjacent:

1. what subject is being offered
2. who the intended audience is
3. what preview fields will be visible before local parse
4. which governance fields remain sealed until local parse
5. what role/capability is actually being offered
6. what redemption, approval, expiry, and reuse posture applies
7. what receipt later proves the issued artifact and its declared constraints

If the sender cannot answer those in one surface, the product is still depending on remembered ritual.

## Public objects

### Offer composer draft

A mutable draft object for composing one portable offer before review.

Suggested fields:

- `offer_composer_draft_id`
- `subject_ref`
- `issuer_ref`
- `audience_scope` (`named-recipient`, `constellation-member`, `constellation-class`, `any-holder`, `handoff-specific`)
- `audience_refs[]`
- `delivery_carriers[]`
- `preview_field_policy_ref`
- `sealed_field_policy_ref`
- `offered_role_profile_ref`
- `approval_policy_ref`
- `expiry_policy_ref`
- `redemption_budget_ref`
- `publication_effect_summary`
- `draft_findings[]`
- `created_at`
- `updated_at`

### Offer issuance review

A prepared review object that explains what issuing this draft will mean.

Suggested fields:

- `offer_issuance_review_id`
- `offer_composer_draft_ref`
- `subject_ref`
- `issuer_ref`
- `current_preview_contract`
- `current_governance_contract`
- `audience_summary`
- `issuance_effect_summary`
- `issuance_non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Offer issuance receipt

A durable receipt proving exactly what artifact was issued and with what declared contract.

Suggested fields:

- `offer_issuance_receipt_id`
- `offer_ref`
- `subject_ref`
- `issuer_ref`
- `audience_summary`
- `preview_contract_summary`
- `governance_contract_summary`
- `offered_role_summary`
- `approval_summary`
- `expiry_summary`
- `redemption_summary`
- `issued_at`
- `proof_refs[]`

## Fixed review order

Every issuance review should preserve the same section order:

1. **Subject and audience**
2. **Preview and sealed-field contract**
3. **Offered role and local-intake expectation**
4. **Approval, expiry, and redemption posture**
5. **Publication and non-effects**
6. **Receipt promise and reissue posture**

### 1) Subject and audience

This section should answer:

- what subject is being offered
- whether the offer targets one recipient, a member class, or any holder
- whether the offer is intended for a personal constellation, a bounded external recipient, or a wider handoff

The sender should not have to reverse-engineer audience from carrier choice.

### 2) Preview and sealed-field contract

This section should state plainly:

- which hints are visible before local parse
- which governance-bearing fields remain sealed until local parse
- what the preview is meant to be enough for
- what it is not meant to authorize

This is the sender-side companion to the recipient decision ladder.

### 3) Offered role and local-intake expectation

This section should say:

- what role profile is being offered
- whether the recipient still needs claim review to choose local path/materialization
- whether the offer can create visibility only, claim draft only, or a broader reviewed outcome after local parse

The sender should not be able to accidentally emit a role that is stronger than the surrounding language suggests.

### 4) Approval, expiry, and redemption posture

This section should say:

- whether approval is always required, only for first redemption, or never required
- when the offer expires
- how many redemptions or slots exist
- whether redemption by one holder consumes the whole artifact or only one slot

This must stay adjacent to audience and role.
It should not live in a distant `Advanced` drawer.

### 5) Publication and non-effects

This section should say what issuing this offer does **not** do yet.
Examples:

- does not widen durable trust immediately
- does not auto-bind a path on the recipient
- does not make the subject ambiently visible on every constellation member unless publication policy also says so
- does not convert a recognition hint into accepted authority

### 6) Receipt promise and reissue posture

This section should say:

- which receipt will prove issuance
- how later reissue, revocation, supersession, or narrowing will relate to this artifact
- whether the sender can later prove what preview/governance contract was issued even if the original carrier message is gone

## Dense share-button contract

A compact share affordance may exist, but it must still surface these fixed labels before issue:

- `Audience`
- `Preview shows`
- `Sealed until parse`
- `Offered role`
- `Approval / expiry / uses`
- `Issue`

Anything denser than that is too implicit.

## Cross-surface rules

### Rule 1 — carrier choice must not be governance choice

Choosing `file`, `URI`, `clipboard`, or `QR` may change delivery ergonomics.
It must not silently change permission or approval semantics unless the surface says so explicitly.

### Rule 2 — role choice must not hide behind key-class lore

AnonSync should not require the sender to remember a secret alphabet of key classes to achieve ordinary least privilege.
The public surface should say `observer`, `reviewable claim`, `writer`, `issuer`, or similar role language directly.

### Rule 3 — single-file and folder offers may differ, but the issuance review must stay grammatically the same

Different subjects may support different expiry or reuse rules.
The product should still present them through the same six-section issuance review instead of a completely different mini-product.

### Rule 4 — issuance must preview non-effects as aggressively as effects

The sender should see what the artifact will **not** do with equal clarity, especially when convenience might tempt them to over-assume publication, acceptance, or trust widening.

## CLI/TUI parity

Textual surfaces should preserve the same adjacency, for example:

```text
Subject: finance-q2
Audience: Maya only
Preview shows: label, approximate size
Sealed until parse: role, expiry, redemption budget
Offered role: reviewable observer claim
Approval / expiry / uses: approval required, expires in 7 days, 1 redemption slot
Issue effect: emits portable offer only; no trust widened yet
Next: issue reviewed artifact
```

## Acceptance test

The issuance surface is good enough when a cautious sender can answer all of the following without leaving one review pane:

- who exactly is this for
- what will be visible before local parse
- what remains sealed until local parse
- what role is actually being offered
- what constraints govern redemption
- what later receipt proves the issued contract
