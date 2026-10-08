# Imported reply referent slice, quote scope, and request coverage interface spec

## Problem it solves

`259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`
answered:

> what exact artifact, correction notice, or replacement object did this imported acknowledgment bind to?

`262-imported-reply-stance-conditionality-and-followup-class-interface-spec.md`
answered:

> what does this reply actually mean, and what is the smallest honest next move now?

But one adjacent seam still remained too easy to flatten:

> **what portion of the larger packet or request did this reply actually refer to?**

Those are not the same truth.

A reply may be exact about the right outward artifact and still speak only about:

- one quoted paragraph or sentence
- one line or range inside a diff-like artifact
- one attachment or attached log
- one named request item inside a larger checklist
- one corrected field such as redaction, time window, or startup-owner note
- one visible subset while leaving the remainder untouched or explicitly open

If AnonSync flattens all of those into one generic `artifact acknowledged` or `request accepted`, it lies in one of two directions:

- it promotes quote-scoped or attachment-scoped feedback into whole-packet acceptance
- or it throws away operationally crucial partial truth such as `timeline paragraph accepted but route attachment still open`

This document defines one explicit **referent-slice / quote-scope / request-coverage** contract so AnonSync can keep
`what exact object was acknowledged?`
separate from
`who can it speak for?`
separate from
`was any human response actually proved?`
separate from
`what stance did that reply create?`
separate from
`what portion of the larger packet or request did the reply actually cover?`
separate from
`which reply is currently operative now once several replies accumulate?`

`264-imported-reply-series-head-register-supersession-and-contradiction-interface-spec.md` answers that last currentness seam.

## Why this deserves first-class treatment

The comparison pressure that made this worth stealing came from three places:

- **Goldenrule** reinforced that citation heads and quoted sub-surfaces should not silently inherit whole-document meaning.
- **DeriveBSD** reinforced that exact scope and exact target claims should stay visible instead of being smoothed into a generic success lane.
- **pyCausalWeave** reinforced that a live reply/request object can still need one additional split between full object identity and the narrower slice the current review actually addressed.

Current review platforms reinforce the same law from a different domain: one review can leave an overall `Comment`, `Approve`, or `Request changes` status while also attaching comments to one file, one specific line, or a multi-line range.
That means a truthful product must preserve **referent slice** instead of inferring whole-request coverage from the mere existence of an exact human reply.

## Core doctrine

For imported replies, **object binding, represented scope, authorship class, reply stance, and referent coverage are orthogonal truths**.

A reply can be:

- exact about the outward artifact,
- exact about the actor or lane,
- strongly human-authored,
- semantically clear in stance,
- and still only cover one quoted/requested slice instead of the whole packet.

AnonSync should therefore preserve at least these distinct answers:

1. whether the reply referred to the whole artifact, one quoted excerpt, one attachment, one line/range, one named request item, or only a visible subset
2. whether the current reply covers one slice only, a named subset, all explicit request items, or the whole outward artifact
3. whether the remainder is unmentioned, explicitly left open, explicitly rejected, or actually closed
4. what stronger proof would justify promoting the current subset truth to whole-artifact or whole-request acceptance
5. how that subset truth combines with object exactness, audience scope, human-proof, and reply stance without overwriting any of them

If `human replied about the right packet` still has to impersonate `human accepted the whole corrected packet`, the interface is not honest enough.

## Objects

### Recipient-referent slice row

A compact row classifying what portion of one outward artifact family an imported reply actually addressed while preserving coverage ceiling and remainder posture.

Suggested fields:

- `recipient_reply_referent_row_id`
- `artifact_family_ref`
- `target_scope_ref`
- `ack_source_ref`
- `binding_row_ref` nullable
- `scope_row_ref` nullable
- `authorship_row_ref` nullable
- `stance_row_ref` nullable
- `referent_scope` (`whole-artifact`, `named-subobject`, `quoted-excerpt-only`, `line-or-range-only`, `attachment-only`, `request-item-only`, `named-subset`, `unclear-subset`, `unknown`)
- `referent_descriptors[]`
- `request_coverage_ceiling` (`none`, `one-slice-only`, `named-subset-only`, `all-explicit-request-items`, `whole-artifact`, `unknown`)
- `remainder_posture` (`no-remainder`, `remainder-unmentioned`, `remainder-explicitly-open`, `remainder-explicitly-rejected`, `unknown`)
- `promotion_requirement` (`explicit-whole-packet-reply`, `all-items-answered`, `new-replacement-ack`, `same-lane-whole-artifact-proof`, `manual-review`, `none`, `unknown`)
- `created_at`

### Referent-slice receipt

A durable receipt proving that one imported reply was classified for referent-slice / coverage truth against one artifact family and one target scope.

Suggested fields:

- `reply_referent_slice_receipt_id`
- `artifact_family_ref`
- `target_scope_ref`
- `ack_source_ref`
- `from_referent_scope`
- `to_referent_scope`
- `request_coverage_ceiling`
- `remainder_posture`
- `promotion_requirement`
- `supporting_refs[]`
- `created_at`

## Interface sections

Any client rendering imported reply coverage for one artifact family and one expected target should preserve this order:

1. **Object / scope / authorship / stance companions**
2. **Current referent slice**
3. **Current request-coverage ceiling**
4. **Remainder posture**
5. **What stronger proof would close the remainder**
6. **Receipts and next honest action**

### 1) Object / scope / authorship / stance companions

Show the current companion answers from `259`, `260`, `261`, and `262`:

- what exact object the reply appears to bind to
- who that reply can speak for
- whether the reply is machine-authored, mixed, or human-authored
- what stance the reply currently carries

This section answers:

**what kind of reply is this, and what stronger foundations already exist around it?**

### 2) Current referent slice

Show one visible referent scope:

- `whole artifact`
- `named subobject`
- `quoted excerpt only`
- `line or range only`
- `attachment only`
- `request item only`
- `named subset`
- `unclear subset`
- `unknown`

This section answers:

**what portion of the outward artifact did the reply actually talk about?**

### 3) Current request-coverage ceiling

Show one current coverage ceiling:

- `none`
- `one slice only`
- `named subset only`
- `all explicit request items`
- `whole artifact`
- `unknown`

This section exists because exact object binding still does not tell the operator how much of the packet or checklist is actually covered.

### 4) Remainder posture

Show:

- whether any remainder still exists
- whether that remainder was merely unmentioned
- whether the reply explicitly left the remainder open or explicitly rejected some remainder
- whether the remainder is now truly closed

This section answers:

**what, if anything, still remains open after this subset reply?**

### 5) What stronger proof would close the remainder

Show:

- whether explicit whole-packet acceptance is still missing
- whether each request item still needs its own answer
- whether a new replacement artifact must be issued and re-acknowledged
- whether only same-lane whole-artifact proof would justify promotion

This section exists so the product does not merely say `not enough yet`; it says exactly what kind of stronger reply or proof would matter.

### 6) Receipts and next honest action

Show:

- referent-slice receipts
- linked binding/scope/authorship/stance receipts
- next honest action (`keep subset-safe state`, `issue narrowed follow-up`, `request whole-packet confirmation`, `record remainder open`, `manual review`, `other`)

## Rules

### Rule 1 — exact artifact binding is not whole-artifact coverage

A reply may bind exactly to the right correction notice or replacement packet and still only address one quoted excerpt, one attachment, or one request item.
Exact binding may strengthen object truth, but it must not silently upgrade coverage to `whole-artifact`.

### Rule 2 — quoted or line-scoped feedback remains slice-scoped until widened

If a reply is visibly anchored to one quoted paragraph, one line, or one selected range, the default referent scope should stay slice-scoped unless stronger evidence explicitly widens it.

### Rule 3 — silence about the remainder is not approval of the remainder

If the reply talks about one visible slice and says nothing about the rest, the untouched remainder should default to `remainder-unmentioned` or `remainder-explicitly-open` rather than inheriting approval.

### Rule 4 — one attachment answer is not whole-packet acceptance

A reply about one log, one attachment, one screenshot, or one appendix must not, by itself, prove that the full packet was accepted.

### Rule 5 — stance and coverage remain separate

A reply may `acknowledge understanding` or even `conditionally accept` and still apply only to one subset of the larger packet.
Likewise, a whole-artifact reply may still carry a blocking stance.
Stance truth and coverage truth must remain separate answers.

### Rule 6 — all-request-items coverage is not always whole-artifact coverage

Some packets contain background explanation, provenance, or optional annexes in addition to explicit requested items.
A reply that clearly covers all explicit request items may still fall short of proving that the recipient accepted every byte or annex of the whole artifact.

## CLI sketch

```text
anonsync ack referent show --family <artifact-family> --target <target>
anonsync ack referent import --family <artifact-family> --target <target> --from <source>
anonsync ack referent classify --ack <ack-source> --scope quoted-excerpt-only --coverage one-slice-only
anonsync ack referent receipt show <receipt>
```

## Example states

- `Vendor replies: “The narrowed timeline redaction looks correct now.”` → scope `quoted-excerpt-only` or `named-subobject`, coverage `one-slice-only`, remainder `remainder-unmentioned`
- `Reviewer comments on lines 48–55 only` → scope `line-or-range-only`, coverage `one-slice-only`, remainder `remainder-unmentioned`
- `Vendor replies: “Attachment B is sufficient; attachment C is still missing.”` → scope `named-subset`, coverage `named-subset-only`, remainder `remainder-explicitly-open`
- `Human reply says “All three requested items are covered; we can proceed.”` → coverage `all-explicit-request-items`, with whole-artifact still depending on broader packet structure
- `Human reply says “The replacement packet as a whole is accepted.”` → scope `whole-artifact`, coverage `whole-artifact`, remainder `no-remainder`

## Anti-goals

This spec does not:

- create a generic code-review or ticketing product
- replace exact-object binding from `259`
- replace actor-scope and audience-ceiling truth from `260`
- replace human-proof and automation classification from `261`
- replace reply stance, blocking effect, or follow-up class from `262`
- infer whole-packet approval from silence alone

## Companion surfaces

- `259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`
- `260-imported-acknowledgment-actor-scope-delegation-and-audience-ceiling-interface-spec.md`
- `261-imported-acknowledgment-authorship-automation-classification-and-human-proof-interface-spec.md`
- `262-imported-reply-stance-conditionality-and-followup-class-interface-spec.md`
- `253-shareable-artifact-carryforward-delta-ledger-and-refresh-notice-interface-spec.md`
- `258-issued-artifact-correction-notice-supersession-and-residual-reliance-interface-spec.md`
