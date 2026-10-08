# Imported acknowledgment authorship, automation classification, and human-proof interface spec

## Problem it solves

`259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`
answered:

> what exact artifact, correction notice, or replacement object did this imported acknowledgment bind to?

`260-imported-acknowledgment-actor-scope-delegation-and-audience-ceiling-interface-spec.md`
answered:

> who can this acknowledgment honestly speak for?

But one adjacent seam still remained too easy to flatten:

> **was this reply human-authored, automation-authored, or only a lane-level automatic reaction?**

Those are not the same truth.

An imported message may be:

- one human-authored reply from the expected actor or lane
- one shared-mailbox automatic out-of-office response
- one ticket-system auto-create or rule-authored comment
- one gateway challenge or bounce-like machine message
- one mixed reply where a human forwarded or edited an automated template
- one receipt-like machine signal that proves lane ingestion but not human review

If AnonSync flattens all of those into `recipient acknowledged`, it lies in one of two directions:

- it promotes machine-authored traffic into human acknowledgment
- or it throws away useful weaker truth such as `lane auto-response observed`, `ticket auto-created`, or `mailbox auto-reply active`

This document defines one explicit **acknowledgment authorship / automation / human-proof** contract so AnonSync can keep
`what object was acknowledged?`
separate from
`who can it speak for?`
separate from
`was any human response actually proved?`

## Why this deserves first-class treatment

The comparison pressure that made this worth stealing came from three places:

- **SlopOS** reinforced that authorship buckets are the first honest discovery lens whenever several parties or mechanisms can author nearby-looking facts.
- **Rust-Needs-and-Dreams** reinforced that session honesty matters: one machine-generated event inside the right loop is still not the same as one human-reviewed step.
- **pyCausalWeave** reinforced that execution identity and responsibility identity should not collapse into one overloaded status word.

Current real-world mail and ticket lanes reinforce the same law:
mail clients can send automatic out-of-office replies, and ticketing/automation systems can send notifications or create comments automatically.
That means a truthful product must preserve **message authorship class** instead of inferring human review from the mere existence of a reply-shaped artifact.

## Core doctrine

For imported acknowledgments, **object binding, represented scope, and authorship class are orthogonal truths**.

A reply can be:

- exact about the object,
- exact about the actor or lane,
- but still only automation-authored,
- or mixed enough that human proof remains absent.

AnonSync should therefore preserve at least these distinct answers:

1. whether the imported artifact was human-authored, automation-authored, mixed, or unknown
2. what automation shape it appears to be (`vacation-reply`, `ticket-auto-create`, `rule-authored-comment`, `gateway-challenge`, `receipt-only`, `other`)
3. whether any explicit human-authored material is present in the imported evidence
4. what current authorship claim ceiling is justified
5. what stronger proof would justify promoting the ceiling to `human responded`
6. how that ceiling combines with object exactness and audience scope without overwriting either

If `same thread`, `same mailbox`, or `ticket exists` still has to impersonate `a human reviewed this and replied`, the interface is not honest enough.

## Objects

### Recipient-acknowledgment authorship row

A compact row classifying one imported acknowledgment for authorship truth while preserving automation class, human-proof state, and current promotion ceiling.

Suggested fields:

- `recipient_ack_authorship_row_id`
- `artifact_family_ref`
- `target_scope_ref`
- `ack_source_ref`
- `presented_sender_ref` nullable
- `reply_lane_kind`
- `authorship_class` (`human-authored`, `automation-authored`, `mixed-human-plus-automation`, `receipt-only-machine-signal`, `unknown`)
- `automation_kind` (`vacation-reply`, `ticket-auto-create`, `rule-authored-comment`, `gateway-challenge`, `delivery-failure-notice`, `read-or-delivery-receipt`, `other`, `none`, `unknown`)
- `human_material_presence` (`explicit-human-text`, `manual-forward-or-quote`, `machine-template-only`, `unknown`)
- `human_proof_strength` (`none`, `weak-human-hint`, `manual-classified`, `structural-human-proof`, `same-product-human-proof`, `unknown`)
- `authorship_claim_ceiling` (`machine-lane-reaction-only`, `lane-ingestion-probable`, `ticket-opened-or-routed`, `human-response-probable`, `human-response-exact`, `unknown`)
- `stronger_human_proof_needed` (`manual-human-reply`, `quoted-object-response`, `ticket-agent-human-comment`, `same-product-seat-proof`, `manual-classification`, `none`, `unknown`)
- `created_at`

### Acknowledgment authorship receipt

A durable receipt proving that one imported acknowledgment was classified for authorship/automation truth against one expected target or audience.

Suggested fields:

- `ack_authorship_receipt_id`
- `artifact_family_ref`
- `target_scope_ref`
- `ack_source_ref`
- `from_authorship_claim_ceiling`
- `to_authorship_claim_ceiling`
- `authorship_class`
- `automation_kind`
- `human_material_presence`
- `human_proof_strength`
- `supporting_refs[]`
- `created_at`

## Interface sections

Any client rendering imported acknowledgment truth for one artifact family and one expected target should preserve this order:

1. **Presented reply and authorship class**
2. **Automation shape and lane reaction truth**
3. **Human-proof state**
4. **Current authorship ceiling**
5. **Exact object binding and audience-scope companions**
6. **Receipts and next honest action**

### 1) Presented reply and authorship class

Show:

- the visible sender or lane the acknowledgment appeared through
- whether the imported artifact appears human-authored, automation-authored, mixed, receipt-only, or unknown
- whether the classification was structural or manual

This section answers:

**what kind of reply artifact is this, before we infer meaning from it?**

### 2) Automation shape and lane reaction truth

Show:

- whether the reply looks like a vacation responder, ticket auto-create, rule-authored comment, gateway challenge, delivery failure, or receipt-like signal
- whether the imported artifact proves only that the lane reacted automatically
- whether the most honest reading is `mailbox auto-response active`, `ticket auto-created`, `rule posted comment`, `delivery failed`, or similar machine truth

This section exists because machine reaction is often useful, but it is not human acknowledgment.

### 3) Human-proof state

Show:

- whether explicit human-written material appears in the imported evidence
- whether a human seems only plausible, manually asserted, structurally proven, or still absent
- whether stronger proof would require a fresh human reply, a quoted response, or same-product proof

This section answers:

**what actual evidence do we have that a human reviewed or answered?**

### 4) Current authorship ceiling

Show one visible ceiling:

- `machine lane reaction only`
- `lane ingestion probable`
- `ticket opened or routed`
- `human response probable`
- `human response exact`
- `unknown`

This ceiling may combine with object-binding exactness from `259` and scope/delegation truth from `260`, but it must remain a separate answer.

### 5) Exact object binding and audience-scope companions

Link the companion answers from `259` and `260`:

- what exact object was acknowledged
- what scope that reply can honestly speak for
- whether the reply is object-exact but only machine-authored
- whether the reply is lane-exact but still lacks human proof

This section answers:

**what object, what scope, and what human-proof level do we actually have?**

### 6) Receipts and next honest action

Show:

- acknowledgment-authorship receipts
- linked acknowledgment-binding rows/receipts
- linked acknowledgment-scope rows/receipts
- next honest action (`keep machine-only`, `classify ticket auto-create`, `wait for human reply`, `import same-product proof`, `manual-upgrade with reason`, `other`)

## Rules

### Rule 1 — reply-shaped traffic is not automatically human acknowledgment

A message that looks like a reply must not, by itself, prove that a human reviewed or acknowledged the object.
Automatic out-of-office replies, ticket auto-create notices, rule-authored comments, and receipt-like machine signals must default to machine ceilings unless stronger evidence exists.

### Rule 2 — useful machine reactions should stay useful

Machine-authored traffic should not be discarded merely because it is not human.
It may still prove lane ingestion, mailbox auto-response posture, ticket creation/routing, or delivery failure.
The surface must preserve those weaker truths explicitly.

### Rule 3 — object exactness does not rescue missing human proof

A machine-authored reply may quote the exact artifact id or correction notice.
That can strengthen object binding.
It must not, by itself, promote the authorship ceiling to `human response probable` or `human response exact`.

### Rule 4 — audience scope does not rescue missing human proof

A reply may come through the exact mailbox or ticket lane.
That can strengthen target-scope truth.
It must not, by itself, prove that a human inside that lane reviewed the object.

### Rule 5 — mixed messages preserve both sides

If one imported artifact contains obvious machine scaffolding plus visible human-authored material, AnonSync should classify it as mixed instead of forcing either `human` or `automation` as the sole truth.

### Rule 6 — manual promotion must preserve the weaker raw facts

Operators may promote a message to stronger human proof when outside evidence justifies it.
That promotion must preserve the original automation classification and weaker structural evidence rather than rewriting history.

## CLI sketch

```text
anonsync ack authorship show --family <artifact-family> --target <target>
anonsync ack authorship import --family <artifact-family> --target <target> --from <source>
anonsync ack authorship classify --ack <ack-source> --class automation-authored --kind vacation-reply
anonsync ack authorship receipt show <receipt>
```

## Example states

- `support@vendor.example receives an automatic out-of-office reply from the expected mailbox` → scope may still be lane-relevant, but authorship ceiling remains `machine lane reaction only`
- `ticket system sends an auto-create notice with case id and no human text` → useful proof of lane ingestion / ticket opening, not human acknowledgment
- `ticket system later posts a comment clearly authored by one named agent` → authorship may rise to `human response probable` or stronger, while scope still depends on `260`
- `same-product successor proof arrives from one exact seat` → authorship may rise to `same-product-human-proof` or `human response exact` if the proof chain warrants it
- `a forwarded auto-reply plus one manual sentence from a human operator arrives` → classify as `mixed-human-plus-automation`, preserving both the machine context and the manual human hint

## Anti-goals

This spec does not:

- create a generic email client or ticketing product
- infer human review from every reply-shaped artifact
- replace exact-object binding from `259`
- replace actor-scope and audience-ceiling truth from `260`
- discard weaker machine truths that are still operationally useful

## Companion surfaces

- `242-fact-authorship-buckets-lane-exactness-and-non-inference-interface-spec.md`
- `252-outbound-channel-execution-delivery-witness-and-claim-ceiling-interface-spec.md`
- `257-shareable-artifact-disclosure-queue-issued-head-and-current-surface-interface-spec.md`
- `259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`
- `260-imported-acknowledgment-actor-scope-delegation-and-audience-ceiling-interface-spec.md`
