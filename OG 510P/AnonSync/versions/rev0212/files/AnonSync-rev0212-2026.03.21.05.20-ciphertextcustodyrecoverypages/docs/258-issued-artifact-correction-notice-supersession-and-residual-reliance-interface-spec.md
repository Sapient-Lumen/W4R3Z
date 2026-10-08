# Issued-artifact correction notice, supersession, and residual-reliance interface spec

## Purpose

The archive already separates:

- current shareable head from current issued head
- queued issue from executed issue
- executed issue from stronger delivery witness
- carryforward explanation from outward currentness
- local evidence from frozen outward packets

One outward seam still remained too easy to reconstruct by hand:

> once an artifact was already issued outwardly and later needs to be **superseded, withdrawn, corrected, or explicitly marked not-current anymore**, what exact surface says which notice now controls, what replacement if any exists, and what the product still does **not** know about older copies or recipient interpretation?

This document turns that seam into one explicit contract.
It is the outward-correction companion to `252-outbound-channel-execution-delivery-witness-and-claim-ceiling-interface-spec.md`, `253-shareable-artifact-carryforward-delta-ledger-and-refresh-notice-interface-spec.md`, and `257-shareable-artifact-disclosure-queue-issued-head-and-current-surface-interface-spec.md`.

## Why this needs its own spec

Cross-reading the companion datacubes sharpened a distinction AnonSync should keep explicit:

- **The Election Stack** showed that a changed public answer is not fully modeled until the product can point to the **superseding notice** that now tells people how to interpret older stale material
- **EvidenceVault** reinforced that candidate queue state, executed outward release, and stable outward explanation are different objects with different jobs
- AnonSync's own disclosure-register and carryforward work already implies the same law, but had not yet stated it cleanly for already-issued artifacts that must later be corrected or withdrawn

The product should therefore answer one explicit question in one place:

- what older issued artifact is being corrected
- whether the correction is **replacement**, **withdrawal without replacement**, or **interpret-with-caveat**
- which correction notice now controls interpretation
- whether a newer replacement artifact has actually been issued yet
- what residual-reliance posture still remains for older copies
- what stronger recipient-side proof would let the product say more than `notice issued` or `replacement issued`

If the operator still has to infer from lineage arrows, current issued head, or remembered chat context whether a previously issued artifact is now superseded, withdrawn, or still likely to be relied on by others, the surface is not explicit enough.

## Core rule

For already-issued outward artifact families, **supersession or withdrawal is its own outward correction object**.

A newer shareable head, a newer issued head, or an internal decision that the older artifact should no longer be used does **not** by itself prove:

1. that recipients were told how to interpret the older artifact now
2. that the older artifact was successfully recalled
3. that a replacement was actually issued
4. that recipients acknowledged the supersession or withdrawal
5. that any stale copy stopped circulating

The operator must be able to answer ten questions in one place:

1. which older issued artifact is being corrected
2. what correction mode now applies
3. whether a replacement artifact exists and whether it was actually issued
4. which correction notice now controls interpretation
5. whether the notice merely warns, actively withdraws, or declares a replacement current
6. what residual reliance posture still remains for older copies
7. which channels make recall impossible or weak
8. whether any stronger recipient acknowledgment exists
9. what tempting overclaim is being refused
10. which receipt later proves correction-state change

If `newer artifact exists` or `we decided to withdraw it` still has to impersonate `the other side now understands the old one as superseded`, AnonSync has not made outward correction honest enough.

## Public objects

### Issued-artifact correction register

A compact object describing one outward artifact family for one recipient or audience together with the currently corrected historical head, the active correction notice if any, any replacement already issued, and the current residual-reliance posture.

Suggested fields:

- `issued_artifact_correction_register_id`
- `artifact_family_ref`
- `target_scope_ref`
- `previous_issued_head_ref` nullable
- `current_issued_head_ref` nullable
- `active_correction_notice_ref` nullable
- `replacement_issued_head_ref` nullable
- `correction_mode` (`none`, `supersede-with-replacement`, `withdraw-without-replacement`, `interpret-with-caveat`, `pending-correction`, `ambiguous`, `unknown`)
- `residual_reliance_posture` (`none-known`, `older-copy-may-still-circulate`, `unrecallable-channel`, `recipient-ack-missing`, `recipient-ack-imported`, `same-product-successor-observed`, `ambiguous`, `unknown`)
- `correction_claim_ceiling` (`internal-decision-only`, `notice-issued`, `replacement-issued`, `recipient-ack`, `same-product-successor-observed`, `unknown`)
- `next_honest_action`
- `generated_at`

### Artifact correction notice

A frozen outward-facing notice or wrapper telling one target or audience how to interpret one older issued artifact now.

Suggested fields:

- `artifact_correction_notice_id`
- `artifact_family_ref`
- `target_scope_ref`
- `corrects_artifact_ref`
- `notice_kind` (`replacement-notice`, `withdrawal-notice`, `caveat-note`, `deprecation-note`, `other`)
- `replacement_artifact_ref` nullable
- `correction_summary`
- `recipient_safe_text`
- `channel_plan[]`
- `recall_limit_note`
- `frozen_at`

### Residual reliance row

A row classifying why older copies or interpretations may still matter even after a correction notice or replacement exists.

Suggested fields:

- `residual_reliance_row_id`
- `artifact_ref`
- `target_scope_ref`
- `reason` (`email-non-recallable`, `forum-post-already-public`, `downloaded-file-may-persist`, `printed-copy-possible`, `ack-missing`, `same-product-successor-observed`, `recipient-confirmed-old-copy-ignored`, `other`)
- `strength` (`weak`, `medium`, `strong`, `unknown`)
- `supporting_receipt_refs[]`
- `updated_at`

### Correction transition receipt

A durable receipt proving one change in outward correction posture for one target or audience.

Suggested fields:

- `correction_transition_receipt_id`
- `artifact_family_ref`
- `target_scope_ref`
- `from_mode`
- `to_mode`
- `trigger` (`notice-prepared`, `notice-issued`, `replacement-issued`, `recipient-ack-imported`, `same-product-successor-observed`, `withdrawal-recorded`, `ambiguity-cleared`, `unknown`)
- `affected_artifact_ref`
- `replacement_artifact_ref` nullable
- `supporting_refs[]`
- `created_at`

## Interface sections

Any client rendering one outward correction case should preserve this review order:

1. **Older issued artifact and target scope**
2. **Current correction mode**
3. **Active correction notice and replacement state**
4. **Residual reliance posture**
5. **Current claim ceiling and stronger proof boundary**
6. **Receipts and next honest action**

### 1) Older issued artifact and target scope

Show:

- artifact family and target scope
- which older issued artifact is being corrected
- whether that older artifact remains the current issued head, has been replaced, or is only historical now
- when it was last known to be outwardly current

The operator must be able to answer: **which already-issued thing are we correcting for whom?**

### 2) Current correction mode

Show one visible verdict:

- `none`
- `supersede-with-replacement`
- `withdraw-without-replacement`
- `interpret-with-caveat`
- `pending-correction`
- `ambiguous`
- `unknown`

This verdict must not be synthesized from lineage alone.
It should come from the correction register and receipts.

### 3) Active correction notice and replacement state

Show:

- whether a correction notice is only drafted, frozen, queued, issued, or acknowledged
- whether a replacement artifact exists
- whether that replacement artifact merely exists, is queued, or is actually issued
- any recall-limit note attached to the correction notice

This section exists because `replacement prepared` is not the same truth as `replacement issued`, and `replacement issued` is not the same truth as `recipient understands the supersession`.

### 4) Residual reliance posture

Show:

- whether older copies may still circulate
- whether the channel class makes recall impossible or weak
- whether any same-product successor observation exists
- whether the recipient explicitly acknowledged the correction

This section must make the residual-risk reason visible, not just the risk label.

### 5) Current claim ceiling and stronger proof boundary

Show what the product may honestly say now:

- `internal decision only`
- `correction notice issued`
- `replacement artifact issued`
- `recipient acknowledged correction`
- `same-product successor observed`

And show the next stronger proof that would justify a stronger claim.

### 6) Receipts and next honest action

Show:

- correction transition receipts
- any outbound execution or delivery witness rows tied to the correction notice or replacement
- the next honest action (`issue notice`, `issue replacement`, `import acknowledgment`, `leave older copy historical`, `open ambiguity review`, `other`)

## Rules

### Rule 1 — internal supersession is not recipient interpretation

A local decision that an older issued artifact is no longer good enough must not by itself rewrite the outward interpretation state.
The product may record that decision, but until a correction notice or replacement is actually issued the claim ceiling remains weaker.

### Rule 2 — withdrawal without replacement is its own mode

The absence of a newer artifact must not force the product to pretend nothing was ever issued or that correction cannot still happen.
A `withdraw-without-replacement` posture is a real outward state and should render that way.

### Rule 3 — replacement issue and correction notice are different acts

Sometimes a newer artifact itself is enough to carry the correction.
Sometimes the operator needs a separate compact notice explaining how to interpret the older artifact.
The archive should permit both shapes and show which one actually happened.

### Rule 4 — residual reliance stays visible after correction

Even after a notice or replacement is issued, older copies may still circulate.
Email, forum posts, downloads, printed copies, and public mirrors all justify a stronger residual-reliance warning than same-product successor observation alone.

### Rule 5 — stronger proof should upgrade claims explicitly

If the product later imports a recipient acknowledgment, same-product successor redemption, or other strong witness, the correction register may upgrade claim ceiling and residual-reliance posture explicitly.
It must not silently rewrite the historical correction chain.

### Rule 6 — correction history does not erase issue history

The older issued artifact remains part of durable outward history even after it is superseded or withdrawn.
Correction surfaces explain the new interpretation state; they do not delete the earlier issue event.

## CLI / API notes

Suggested CLI verbs:

```text
anonsync artifact correction show --family artfam_01K... --target mailbox:vendor-a
anonsync artifact correction prepare-notice --family artfam_01K... --corrects art_01K... --replacement art_01K... --target mailbox:vendor-a
anonsync artifact correction issue-notice corr_01K...
anonsync artifact correction import-ack corr_01K... --source mail-reply.eml
```

Suggested API additions live best beside artifact disclosure, channel execution, and carryforward resources rather than inside lineage-only resources.

## Example cases

- `Older vendor packet already issued by email; newer packet exists but has not been sent` → disclosure register may show a newer shareable head, but correction mode remains `none` until a replacement or notice is actually issued
- `Older packet was wrong; operator issues a short correction notice with no replacement yet` → correction mode `withdraw-without-replacement`, claim ceiling `notice-issued`, residual reliance `email-non-recallable`
- `Older packet was replaced and the recipient later replies acknowledging the newer one` → correction mode `supersede-with-replacement`, claim ceiling `recipient-ack`, residual reliance may drop but historical older issue stays visible
- `Same-product offer was reissued and the successor was redeemed` → correction mode `supersede-with-replacement`, claim ceiling `same-product-successor-observed`

## Regressions refused

- letting a newer shareable head quietly imply the old outward artifact is now understood as obsolete
- letting `withdrawn locally` imply successful recall from email, forum, or downloaded-file channels
- letting a correction notice erase the earlier issue event
- forcing `replacement exists` and `recipient interpreted replacement as current` to be the same status chip
- hiding residual stale-copy risk once a correction was merely prepared or queued

## Relationships

This document builds on:

- `140-external-escalation-packet-and-redaction-review-interface-spec.md`
- `247-shareable-artifact-lineage-head-register-and-warning-surface-interface-spec.md`
- `252-outbound-channel-execution-delivery-witness-and-claim-ceiling-interface-spec.md`
- `253-shareable-artifact-carryforward-delta-ledger-and-refresh-notice-interface-spec.md`
- `257-shareable-artifact-disclosure-queue-issued-head-and-current-surface-interface-spec.md`
- `259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`
- `260-imported-acknowledgment-actor-scope-delegation-and-audience-ceiling-interface-spec.md`
