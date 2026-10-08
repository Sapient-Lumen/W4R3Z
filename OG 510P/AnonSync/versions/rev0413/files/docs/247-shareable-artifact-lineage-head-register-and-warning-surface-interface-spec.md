# Shareable-artifact lineage head register and warning surface interface spec

## Purpose

The archive already has portable offer lineage, successor boundaries, continuity bundles, held-unsent escalation packets, and frozen reviewed manifests.
What still remained too easy to reconstruct by hand was a smaller but important question:

> when several retained artifacts now belong to one lineage or family, which one is merely the latest working tip, which one is actually the current frozen shareable head, and what warning blocks a unique answer?

This document turns that question into one explicit interface contract.
It is the compact-head companion to `116-offer-reissue-lineage-and-successor-boundary-interface-spec.md`, the packet-family companion to `140-external-escalation-packet-and-redaction-review-interface-spec.md`, and the durable-surface companion to `232-diagnostic-export-log-redaction-and-self-serve-support-boundary-interface-spec.md`.

## Core rule

Retained shareable artifacts need one tiny **head register**.

The product is not fully inspectable until it can answer six questions in one place:

1. which artifact family or lineage is in view
2. which retained artifacts are roots, tips, superseded members, or branches
3. which tip is the current **operational head**
4. which frozen artifact, if any, is the current **shareable head**
5. what warning blocks a unique shareable answer (`not frozen`, `branched`, `expired`, `sent-but-superseded`, `missing-proof`, or `unknown`)
6. which stable current surface should a cautious operator open right now for this family

If the operator still has to inspect several retained packets, offers, or bundles just to answer **which one is current enough to share**, the archive is leaving lineage meaning in folklore.

## Why this needs its own spec

AnonSync already retains multiple families of artifacts that can outlive one moment of use:

- predecessor and successor offer artifacts
- frozen escalation packets and later recipient-specific revisions
- continuity bundles and salvage bundles
- shareable notes or summaries tied to one incident family

Those objects already have lineage, freeze, and receipt language.
What they do not yet share is one compact operator-facing answer to `what should I use right now?`
Cross-reading the companion datacubes sharpened the missing shape:
there should be one tiny register that distinguishes **latest working tip** from **current frozen shareable head** and that preserves warnings when those are not the same.

## Public objects

### Shareable-artifact head row

A compact read object describing one retained artifact family and its current heads.

Suggested fields:

- `shareable_artifact_head_row_id`
- `artifact_family_ref`
- `artifact_kind` (`offer`, `escalation-packet`, `continuity-bundle`, `repair-bundle`, `support-note`, `other`)
- `retained_member_count`
- `root_refs[]`
- `tip_refs[]`
- `operational_head_ref` nullable
- `shareable_head_ref` nullable
- `warning_codes[]`
- `recommended_open_ref` nullable
- `generated_at`

### Shareable-artifact head register

A read object summarizing current heads for one seat, incident, or scope.

Suggested fields:

- `shareable_artifact_head_register_id`
- `seat_ref`
- `scope_ref`
- `rows[]`
- `summary_counts`
- `generation_basis` (`live`, `receipt-reconciled`, `history-rebuilt`)
- `generated_at`

### Shareable-artifact warning row

One ambiguity or missing-proof fact that blocks a clean current-shareable answer.

Suggested fields:

- `shareable_artifact_warning_row_id`
- `artifact_family_ref`
- `warning_kind` (`latest-tip-not-frozen`, `branched-tips`, `shareable-head-expired`, `sent-but-superseded`, `recipient-mismatch`, `missing-freeze-proof`, `unknown`)
- `severity` (`advisory`, `guarded`, `blocking`)
- `summary`
- `suggested_next_action`

### Shareable-head receipt

A durable object proving how a family's current shareable head changed.

Suggested fields:

- `shareable_head_receipt_id`
- `artifact_family_ref`
- `previous_shareable_head_ref` nullable
- `result_shareable_head_ref` nullable
- `transition` (`freeze-new-head`, `supersede-head`, `expire-head`, `clear-ambiguity`, `destroy-head`, `recipient-rebind`)
- `recorded_at`
- `proof_refs[]`

## Operational and shareable heads

### Operational head

The latest retained artifact tip that the product currently treats as the best working object for continued local editing, inspection, or preparation.
An operational head may still be a draft or a not-yet-frozen revision.

### Shareable head

The frozen retained artifact that the product currently treats as the right object to disclose, attach, or point another party at.
A shareable head is stricter than an operational head.
No unique shareable head should be implied unless freeze, audience, and lineage warnings permit it.

## Fixed inspection order

Every head-register surface should preserve this order:

1. **Artifact family and audience**
2. **Retained members, roots, and tips**
3. **Operational head versus shareable head**
4. **Warnings and blocked uniqueness**
5. **Open current surface, freeze, supersede, or archive**
6. **Receipts and lineage proofs**

### 1) Artifact family and audience

This section should show:

- artifact family id
- artifact kind
- intended audience or recipient class where relevant
- current state summary

The operator must be able to answer: **what family of retained artifacts is this register talking about?**

### 2) Retained members, roots, and tips

This section should show:

- all retained members in compact order
- roots and current tips
- whether the lineage is linear or branched
- whether any members were intentionally destroyed or expired

The operator must be able to answer: **what exists in this family and how did it branch?**

### 3) Operational head versus shareable head

This section should show:

- the latest working tip
- the currently frozen shareable artifact, if unique
- whether they are the same object
- whether the shareable head is older on purpose because the latest tip is not yet frozen or not yet audience-correct

The operator must be able to answer: **which artifact is current for local work, and which one is current for actual sharing?**

### 4) Warnings and blocked uniqueness

This section should show:

- latest tip not frozen
- branched tips
- expired or audience-mismatched shareable head
- sent head now superseded by a later reviewed packet
- missing proof forcing `unknown`

The operator must be able to answer: **why might the current-shareable answer be ambiguous or blocked?**

### 5) Open current surface, freeze, supersede, or archive

This section should show:

- `Open operational head`
- `Open shareable head`
- `Freeze current tip as new shareable head`
- `Supersede prior shareable head`
- `Archive / destroy stale head`

The operator must be able to answer: **what honest next action resolves this family now?**

### 6) Receipts and lineage proofs

This section should show:

- freeze receipts
- supersession receipts
- disclosure receipts where relevant
- predecessor/successor receipts
- any missing proof that forces warnings

The operator must be able to answer: **what later evidence proves why this head is current or not current?**

## Warning rules

### Rule 1 — latest is not always shareable

A draft or unfrozen tip may be the operational head without becoming the shareable head.

### Rule 2 — sent is not always current

A packet or artifact may already have been sent and still no longer be the current shareable head for later use.

### Rule 3 — audience matters

A shareable head for one recipient class is not automatically the shareable head for another.

### Rule 4 — ambiguity should persist as a warning, not be guessed away

If several tips remain live or freeze proof is missing, the register should preserve that ambiguity explicitly.

### Rule 5 — opening a head register must not mutate lineage

Inspection alone must not freeze, send, supersede, or destroy artifacts.

## Dense row contract

A dense row should preserve these labels in this order:

- `Family`
- `Tips`
- `Operational head`
- `Shareable head`
- `Warnings`
- `Next action`

## CLI contract

Minimal commands:

```text
anonsync artifact heads list --scope outgoing
anonsync artifact heads show --family pktfam_01J...
anonsync artifact heads open --family pktfam_01J... --which shareable
anonsync artifact heads freeze-current --family pktfam_01J... --plan
```

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following without manually comparing lineage prose:

- which retained artifact is the latest working tip
- which retained artifact is the current frozen shareable head
- whether those are the same object
- what warning blocks a unique current-shareable answer
- what receipt later proves the answer


## Companion

- `252-outbound-channel-execution-delivery-witness-and-claim-ceiling-interface-spec.md`
- `253-shareable-artifact-carryforward-delta-ledger-and-refresh-notice-interface-spec.md`
- `257-shareable-artifact-disclosure-queue-issued-head-and-current-surface-interface-spec.md`
