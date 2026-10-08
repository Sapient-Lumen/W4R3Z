# Outbound channel execution, delivery witness, and claim-ceiling interface spec

## Purpose

The archive already has:

- delivery encoding is not authority semantics
- local evidence versus frozen shareable packet separation
- durable confirmation versus transient UI delivery
- shareable-artifact head registers
- local-web history witness and non-replay rules

What still remained under-specified was a subtler outbound seam:

> once a portable offer, snapshot, or escalation packet is already reviewed and frozen, what does each **channel action** actually prove, what does it definitely not prove yet, and when may the product speak as if anything was truly sent, delivered, or received?

That seam matters because different channel completions mean different things:

- copying to the clipboard proves local clipboard state, not that anyone pasted it
- invoking a platform share sheet is not always the same thing as the target receiving the bytes
- materializing a browser download or save-as file is still local custody, not recipient receipt
- creating a `mailto:` or export attachment does not prove the message was actually sent
- a later same-product redeem or imported acknowledgment is a stronger witness than any of the above

This document defines one first-class **outbound channel execution** object, one **delivery witness** object, and one explicit **claim ceiling** row so AnonSync stops flattening `prepared`, `copied`, `shared`, `exported`, `sent`, and `received` into one success chip.

## Core rule

Every outward movement of a reviewed shareable artifact must keep six truths separate:

1. which exact frozen artifact was current
2. which channel was chosen
3. what local execution the product actually observed
4. what the strongest current delivery witness is
5. what the current claim ceiling allows the product to say
6. what stronger claim would require another witness

The product must not let a green local channel completion silently turn into `sent` or `delivered` when the channel only proved a weaker fact.

## Why this needs its own spec

Existing docs already separate offer meaning from delivery encoding and packet freeze from disclosure.
What they do **not** yet do is publish the truth boundary of the channel action itself.

That gap becomes especially sharp on local web and modern desktop/mobile surfaces where the visible gesture may be one of:

- `Copy`
- `Download`
- `Save packet`
- `Share...`
- `Open mail client`
- `Export attachment`
- `Hand off to another local tool`

Those gestures are useful.
They are not semantically interchangeable.
A trustworthy product therefore needs one compact channel-execution grammar above them.

## Public objects

### Outbound channel execution

A durable object for one reviewed attempt to move one already-frozen shareable artifact through one channel.

Suggested fields:

- `outbound_channel_execution_id`
- `artifact_family_ref`
- `artifact_ref`
- `artifact_kind` (`portable-offer`, `escalation-packet`, `snapshot-send`, `continuity-bundle`, `other`)
- `channel_kind` (`clipboard-text`, `clipboard-binary`, `browser-download`, `save-as-file`, `web-share`, `mailto-handoff`, `attachment-export`, `local-open-with`, `same-product-peer-handoff`, `network-post`, `unknown`)
- `surface_class` (`local-web`, `desktop`, `headless-cli`, `remote-workbench`, `mobile`, `other`)
- `execution_state` (`prepared`, `invoked`, `locally-completed`, `launched-only`, `target-pass-observed`, `user-aborted`, `platform-blocked`, `failed`, `unknown`)
- `claim_ceiling` (`artifact-ready-only`, `local-channel-completed`, `handoff-launched-only`, `target-pass-observed`, `remote-receipt-imported`, `remote-consumption-confirmed`, `unknown`)
- `artifact_hash`
- `platform_variance_note` nullable
- `created_at`

### Delivery witness row

One fact row describing the strongest currently known evidence that the artifact moved beyond local channel execution.

Suggested fields:

- `delivery_witness_row_id`
- `execution_ref`
- `witness_kind` (`none`, `same-product-redeem`, `recipient-ack-import`, `callback-token`, `operator-attested`, `message-send-confirmed`, `remote-open-confirmed`, `unknown`)
- `witness_source_kind` (`product-observed`, `imported-external-proof`, `operator-attested`, `recipient-supplied`, `unknown`)
- `state` (`absent`, `present`, `contradicted`, `stale`, `unknown`)
- `supports_claim_up_to` (`artifact-ready-only`, `local-channel-completed`, `handoff-launched-only`, `target-pass-observed`, `remote-receipt-imported`, `remote-consumption-confirmed`, `unknown`)
- `ref`
- `observed_at` nullable

### Claim-ceiling row

A compact statement of what the product may honestly say now.

Suggested fields:

- `claim_ceiling_row_id`
- `execution_ref`
- `allowed_label` (`ready`, `copied`, `saved-locally`, `share-invoked`, `passed-to-target`, `receipt-imported`, `received`, `unknown`)
- `forbidden_labels[]`
- `stronger_claim_requires[]`
- `next_honest_action`

## Fixed inspection order

Every outbound channel execution surface should preserve this order:

1. **Which frozen artifact is being moved**
2. **Which channel is being used and from which surface**
3. **What exact local execution was observed**
4. **Current strongest witness beyond local execution**
5. **Current claim ceiling and forbidden stronger labels**
6. **Retry here, switch channel, import witness, or retire execution**

### 1) Which frozen artifact is being moved

This section should name the exact artifact and its current family head posture.
Examples:

- `Escalation packet head epk_01J... frozen for trusted operator question`
- `Offer off_01K... current shareable head`
- `Snapshot send sns_01K... retained for later delivery`

### 2) Which channel is being used and from which surface

Examples:

- `Clipboard text from local web`
- `Browser download from local web`
- `Web share from mobile workbench`
- `Attachment export from desktop`
- `Mail client handoff from desktop`

### 3) What exact local execution was observed

This section should not overstate the channel action.
Examples:

- `Clipboard updated locally`
- `Share sheet launched; platform-specific completion semantics apply`
- `Data passed to share target`
- `Download saved to local path`
- `Mail client opened with attachment draft`

### 4) Current strongest witness beyond local execution

Examples:

- `No witness beyond local clipboard update`
- `Offer later redeemed by same-product recipient`
- `Imported recipient acknowledgment message`
- `User attested external send; no machine witness`

### 5) Current claim ceiling and forbidden stronger labels

Examples:

- `You may say copied; do not say sent or delivered`
- `You may say share invoked; do not say received`
- `You may say passed to target; do not say recipient opened`
- `You may say receipt imported; do not say consumed unless the witness proves it`

### 6) Retry here, switch channel, import witness, or retire execution

Examples:

- `Retry clipboard copy`
- `Switch to saved file instead`
- `Import same-product redeem receipt`
- `Record operator attestation only`
- `Retire stale execution and keep artifact head`

## Public rules

### Rule 1 — channel completion semantics are channel-specific

The product must not use one generic `sent` meaning across clipboard, download, web-share, export, and redeem paths.

### Rule 2 — local completion does not imply recipient receipt

Recipient-target guard stays separate from channel execution: a copied/downloaded/share-invoked row may remain true for the old target even while a newer target is now blocked pending retarget review.


A local save, clipboard update, or generated attachment remains a local-custody truth unless a stronger witness arrives.

### Rule 3 — web-share completion must preserve platform variance

If the platform only proves share-sheet launch, the product must keep that weaker ceiling visible.
If the platform proves data passed to the target, the product may say that and no more.

### Rule 4 — shareable-artifact head and latest channel execution are different objects

The current shareable head answers `what artifact is current for reuse?`
The channel execution answers `what happened in one channel attempt?`
Neither should overwrite the other.

### Rule 5 — imported recipient evidence must not rewrite older weaker history

A later stronger witness may lift the current claim ceiling, but it should not falsify what earlier channel execution actually proved at the time.

### Rule 6 — labels must inherit the current claim ceiling

Buttons, toasts, rows, and CLI output should say `Copied`, `Saved locally`, `Share invoked`, `Passed to target`, or `Receipt imported` when those are the truthful labels.
They should not skip ahead to `Delivered`.

### Rule 7 — no witness is a normal state

A useful outbound action may legitimately end at `artifact frozen and copied locally`.
The product should not force fake certainty merely because the operator chose a manual or privacy-preserving channel.

## Dense row contract

A dense outbound execution row should preserve these labels in this order:

- `Artifact`
- `Channel`
- `Observed`
- `Witness`
- `Ceiling`
- `Next`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following without reconstructing browser, OS, or support folklore:

- which exact frozen artifact was current for this channel action
- what channel was actually used
- what exact local completion the product observed
- whether any stronger witness exists beyond that local completion
- what the product may honestly say right now
- what stronger claim would require another witness
- whether retrying, switching channels, or importing later proof would change the answer


## Companion

- `253-shareable-artifact-carryforward-delta-ledger-and-refresh-notice-interface-spec.md`
- `257-shareable-artifact-disclosure-queue-issued-head-and-current-surface-interface-spec.md`
- `258-issued-artifact-correction-notice-supersession-and-residual-reliance-interface-spec.md`
- `259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`

- `261-imported-acknowledgment-authorship-automation-classification-and-human-proof-interface-spec.md`
