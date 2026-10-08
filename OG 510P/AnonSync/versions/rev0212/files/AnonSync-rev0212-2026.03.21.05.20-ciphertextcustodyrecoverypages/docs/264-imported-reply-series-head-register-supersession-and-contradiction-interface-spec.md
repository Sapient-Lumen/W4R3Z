# Imported reply series head register, supersession, and contradiction interface spec

## Problem it solves

`259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`
answered:

> what exact artifact, correction notice, refresh note, or replacement object did this imported reply bind to?

`260-imported-acknowledgment-actor-scope-delegation-and-audience-ceiling-interface-spec.md`
answered:

> who can this reply honestly speak for?

`261-imported-acknowledgment-authorship-automation-classification-and-human-proof-interface-spec.md`
answered:

> was any human response actually proved?

`262-imported-reply-stance-conditionality-and-followup-class-interface-spec.md`
answered:

> what does this reply mean, and what is the smallest honest follow-up now?

`263-imported-reply-referent-slice-quote-scope-and-request-coverage-interface-spec.md`
answered:

> what portion of the larger packet or request did this reply actually cover?

But one remaining seam was still too easy to leave to thread archaeology:

> when several imported replies now exist in the same lane, **which one is currently operative, which older ones were superseded, and which apparently-latest reply still leaves parallel live blockers or slice-specific heads in place?**

Those are not the same truth.

A later reply may be:

- newer in raw chronology but narrower in scope than an older blocking whole-packet reply
- exact and human-authored but only about one quoted slice
- a later clarification that does not actually supersede an earlier decline
- a same-lane update from one represented actor while another actor-scope head remains live
- an apparent approval that still conflicts with an unresolved earlier request-changes stance on another slice
- a new whole-artifact acceptance that really does supersede one older blocker

If AnonSync flattens all of that into `latest reply wins`, it lies in one of two directions:

- it promotes bottom-most-thread position into current operative truth even when older blockers still remain live
- or it forces operators to reconstruct current reply state manually from raw chronology

This document defines one explicit **reply-series head register** so AnonSync can preserve reply chronology, current operative head, superseded older heads, parallel live heads, and contradiction warnings separately.

## Why this deserves first-class treatment

The comparison pressure that made this worth stealing came from three places:

- **Goldenrule** reinforced that once an archive already has retained objects and lineages, operators still need one tiny head register that answers which tip is merely latest, which tip is currently claim-ready, and where branch or ambiguity warnings block one unique answer.
- **Anonymity** reinforced the value of keeping moving families under one visible series umbrella instead of forcing inheritors to reconstruct currentness from scattered files and queue state.
- **pyCausalWeave** reinforced that current request/review truth often needs one more split between raw arrival order and the narrower current gate or current live blocker that still governs action.

Current official product behavior reinforces the same law from a different domain: Gmail groups replies into one conversation with the latest email at the bottom, but thread order alone does not settle semantic currentness; GitHub separately preserves comment, approve, and request-changes states and can dismiss stale approvals when the diff changes, which shows that review chronology and operative current state are not the same object.

## Core doctrine

For imported replies, **raw chronology is not current operative truth**.

AnonSync should therefore preserve at least these distinct answers:

1. what reply arrived most recently in raw chronology
2. what reply or replies are currently operative for whole-artifact meaning
3. what reply or replies are currently operative only for one quoted slice or named subset
4. which older replies were genuinely superseded
5. which apparently older blockers still remain live because later replies were narrower, actor-different, or conditional
6. whether a unique current head exists at all, or whether the series currently has parallel live heads or contradiction warnings
7. what stronger evidence or explicit manual resolution would collapse the current ambiguity safely

If the operator still has to infer current reply meaning by reading thread bottom-up, the interface is not honest enough.

## Objects

### Recipient-reply series row

A compact row classifying the current operative state of one imported-reply family for one target scope and one represented actor partition.

Suggested fields:

- `recipient_reply_series_row_id`
- `artifact_family_ref`
- `target_scope_ref`
- `represented_actor_scope_ref` nullable
- `series_partition_kind` (`whole-target`, `represented-actor`, `actor-plus-slice`, `target-lane-generic`, `unknown`)
- `member_reply_refs[]`
- `latest_arrival_ref`
- `current_whole_artifact_head_ref` nullable
- `current_subset_head_refs[]`
- `superseded_reply_refs[]`
- `parallel_live_head_refs[]`
- `head_verdict` (`unique-whole-head`, `subset-heads-only`, `whole-plus-subset-heads`, `parallel-live-heads`, `no-current-head`, `unknown`)
- `contradiction_warning` (`none`, `later-narrow-reply-does-not-clear-older-block`, `parallel-same-scope-conflict`, `actor-scope-conflict`, `whole-vs-subset-tension`, `manual-resolution-required`, `unknown`)
- `stronger_resolution_needed` (`explicit-whole-artifact-reply`, `same-actor-clarification`, `new-replacement-reply`, `manual-head-selection`, `none`, `unknown`)
- `created_at`

### Reply-series head receipt

A durable receipt proving that one reply-series head register was rebuilt or reclassified for one artifact family / target scope partition.

Suggested fields:

- `reply_series_head_receipt_id`
- `artifact_family_ref`
- `target_scope_ref`
- `represented_actor_scope_ref` nullable
- `latest_arrival_ref`
- `from_head_verdict`
- `to_head_verdict`
- `current_whole_artifact_head_ref` nullable
- `current_subset_head_refs[]`
- `superseded_reply_refs[]`
- `parallel_live_head_refs[]`
- `contradiction_warning`
- `supporting_refs[]`
- `created_at`

## Interface sections

Any client rendering imported reply currentness for one artifact family and one target should preserve this order:

1. **Series partition and latest arrival**
2. **Current whole-artifact head**
3. **Current subset heads**
4. **Superseded and still-live older replies**
5. **Contradiction warning / no-unique-head state**
6. **Receipts and next honest action**

### 1) Series partition and latest arrival

Show:

- which target / actor / slice partition this register covers
- the newest imported reply in raw chronology
- whether the latest arrival is also the current operative head or merely the newest member of the series

This section answers:

**what conversation family is being summarized, and what arrived last?**

### 2) Current whole-artifact head

Show one visible answer for whole-artifact meaning:

- `none`
- `current whole-artifact accept head`
- `current whole-artifact blocking head`
- `current whole-artifact conditional head`
- `current whole-artifact redirect head`
- `ambiguous / no unique whole-artifact head`

This section answers:

**what reply currently governs whole-packet meaning, if any?**

### 3) Current subset heads

Show any live slice-level or request-item-level heads such as:

- `timeline paragraph accepted`
- `route attachment still blocking`
- `startup-owner note redirected`
- `request item 2 conditionally accepted`

This section exists because current useful reply state may legitimately be a set of subset heads rather than one global whole-artifact answer.

### 4) Superseded and still-live older replies

Show:

- which older replies were genuinely superseded
- which older replies remain live because later replies were narrower, actor-different, or merely clarifying
- whether one older blocker still governs even though a later reply arrived

This section answers:

**what older state stopped mattering, and what older state still matters right now?**

### 5) Contradiction warning / no-unique-head state

Show one visible warning when needed:

- `latest reply is narrower than older blocker`
- `parallel same-scope conflict`
- `whole-vs-subset tension`
- `actor-scope conflict`
- `manual resolution required`

This section exists so the product can say `there is no single current reply head yet` without erasing useful partial truth.

### 6) Receipts and next honest action

Show:

- reply-series head receipts
- linked binding/scope/authorship/stance/referent receipts
- next honest action (`keep blocker head`, `request explicit whole-artifact answer`, `keep subset-safe state`, `manual resolve`, `issue successor packet`, `other`)

## Rules

### Rule 1 — latest arrival is not automatically the current head

The bottom-most email or newest ticket comment may be newer in chronology while still being narrower than an older blocking or whole-artifact reply.
It must not silently replace the older operative head just because it arrived later.

### Rule 2 — subset approval does not automatically clear older whole-artifact blockers

If an earlier reply requested changes on the packet as a whole and a later reply approves only one quoted slice, the older blocker remains live unless stronger evidence explicitly clears it.

### Rule 3 — real supersession needs scope-compatible evidence

A later reply may supersede an older one only when the represented actor scope, object basis, and referent coverage are compatible enough to justify replacement.
If that proof is missing, older live heads should remain visible.

### Rule 4 — one actor's newer head does not erase another actor's head

If different represented actors or delegated scopes replied, each lane may keep its own current head until the product has stronger cross-scope proof.
One lane's later answer must not silently erase another lane's still-live blocker or condition.

### Rule 5 — contradiction should survive honestly

If the series has parallel live heads that cannot be safely collapsed, the head register should say so explicitly instead of forcing one fake winner.

### Rule 6 — history stays readable even after head collapse

Even when one later reply really does supersede an older one, the older reply should remain visible as superseded lineage rather than disappearing from the series.

## CLI sketch

```text
anonsync ack series show --family <artifact-family> --target <target>
anonsync ack series rebuild --family <artifact-family> --target <target>
anonsync ack series classify-head --family <artifact-family> --target <target> --reply <reply-id>
anonsync ack series receipt show <receipt>
```

## Example states

- `latest reply says only "timeline section looks fine" while an older whole-packet request-changes reply is still unresolved` → latest arrival is newer, but current whole-artifact head remains blocking and one subset-accept head also remains live
- `same human later replies "current packet now looks good" after the corrected reissue` → older blocker can become superseded and the current whole-artifact head becomes approving
- `shared mailbox replies from one named agent while another represented group lane still has no answer` → actor-scoped head exists, whole-target head may remain unresolved
- `two same-scope human replies give incompatible current answers` → parallel live heads and contradiction warning remain visible until manual resolution or stronger later reply

## Acceptance tests

1. A later slice-only approval does not silently clear an older whole-packet blocker.
2. A later same-scope whole-artifact approval can supersede an older blocker when object basis and scope match.
3. Two different represented actors can keep parallel live heads without being flattened into one target-wide answer.
4. The register can show `latest arrival` and `current operative head` as different objects.
5. Clients can render the series without requiring thread archaeology.

## See also

- `259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`
- `260-imported-acknowledgment-actor-scope-delegation-and-audience-ceiling-interface-spec.md`
- `261-imported-acknowledgment-authorship-automation-classification-and-human-proof-interface-spec.md`
- `262-imported-reply-stance-conditionality-and-followup-class-interface-spec.md`
- `263-imported-reply-referent-slice-quote-scope-and-request-coverage-interface-spec.md`
- `247-shareable-artifact-lineage-head-register-and-warning-surface-interface-spec.md`
- `253-shareable-artifact-carryforward-delta-ledger-and-refresh-notice-interface-spec.md`
