# Imported reply stance, conditionality, and follow-up class interface spec

## Problem it solves

`259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`
answered:

> what exact artifact, correction notice, or replacement object did this imported acknowledgment bind to?

`260-imported-acknowledgment-actor-scope-delegation-and-audience-ceiling-interface-spec.md`
answered:

> who can this acknowledgment honestly speak for?

`261-imported-acknowledgment-authorship-automation-classification-and-human-proof-interface-spec.md`
answered:

> was this reply human-authored, automation-authored, or only a lane-level automatic reaction?

But one adjacent seam still remained too easy to flatten:

> **what does this reply actually mean, and what is the smallest honest next move now?**

Those are not the same truth.

A human-authored or mixed reply may:

- merely acknowledge receipt
- say it understands the correction or replacement
- ask for clarification or more evidence
- request a changed artifact, narrower redaction, or different format
- redirect the operator to a different mailbox, portal, queue, or lane
- conditionally accept once one further step is completed
- decline, reject, or refuse the request outright

If AnonSync flattens all of those into one generic `recipient acknowledged`, it lies in one of two directions:

- it promotes comments or clarification questions into acceptance
- or it throws away operationally crucial meaning such as `redirected`, `needs more info`, or `request changes before this counts`

This document defines one explicit **reply-stance / conditionality / follow-up-class** contract so AnonSync can keep
`what exact object was acknowledged?`
separate from
`who can it speak for?`
separate from
`was any human response actually proved?`
separate from
`what current stance and next move did that reply actually create?`

## Why this deserves first-class treatment

The comparison pressure that made this worth stealing came from three places:

- **Anonymity** reinforced the idea of response menus and smallest-sufficient follow-up handoffs: once the response object exists, the product still owes one explicit answer to `what exact next packet or action is the smallest honest thing to hand over now?`
- **pyCausalWeave** reinforced that request truth, review truth, and follow-through truth should not collapse into one overloaded `approved` or `done` word.
- **DeriveBSD** reinforced that exact scope and exact outcome should stay visible instead of being smoothed into a generic success lane.

Current review platforms reinforce the same law from a different domain: a human review can be a comment, an approval, or a request for changes.
That means a truthful product must preserve **reply stance** instead of inferring acceptance from the mere existence of a human reply.

## Core doctrine

For imported replies, **object binding, represented scope, authorship class, reply stance, and covered portion are orthogonal truths**.

`263-imported-reply-referent-slice-quote-scope-and-request-coverage-interface-spec.md` now refines whether the current stance applies to the whole outward artifact or only one quoted/requested slice.

A reply can be:

- exact about the object,
- exact about the actor or lane,
- strongly human-authored,
- and still only be a clarification request or redirect rather than acceptance.

AnonSync should therefore preserve at least these distinct answers:

1. whether the reply merely acknowledges receipt, affirms understanding, requests clarification, requests changes, redirects, conditionally accepts, or declines
2. whether the reply blocks the current claim, merely suggests a next move, or reroutes the operator to a new lane
3. what smallest honest follow-up class now applies
4. what stronger response would justify promoting the current stance to `accepted` or `resolved`
5. how that stance combines with object exactness, audience scope, and human-proof without overwriting any of them

If `human replied` still has to impersonate `human accepted this exact replacement and no follow-up remains`, the interface is not honest enough.

## Objects

### Recipient-reply stance row

A compact row classifying one imported reply for semantic stance while preserving block/redirect meaning and smallest-sufficient follow-up class.

Suggested fields:

- `recipient_reply_stance_row_id`
- `artifact_family_ref`
- `target_scope_ref`
- `ack_source_ref`
- `binding_row_ref` nullable
- `scope_row_ref` nullable
- `authorship_row_ref` nullable
- `reply_stance` (`machine-operational-only`, `acknowledges-receipt`, `acknowledges-understanding`, `requests-clarification`, `requests-artifact-change`, `requests-different-channel-or-format`, `redirects-to-different-lane`, `conditionally-accepts-pending-step`, `declines-or-rejects`, `ambiguous`, `unknown`)
- `blocking_effect` (`non-blocking`, `follow-up-required`, `redirect-required`, `current-claim-blocked`, `terminal-decline`, `unknown`)
- `followup_class` (`none`, `answer-clarification`, `issue-corrected-artifact`, `repackage-or-rechannel`, `retarget-lane`, `provide-stronger-proof`, `record-decline-and-stop`, `manual-review`, `unknown`)
- `accepted_scope_ceiling` (`none`, `receipt-only`, `understanding-only`, `conditional-pending-step`, `accepted-current-request`, `redirect-only`, `declined`, `unknown`)
- `stronger_reply_needed` (`explicit-acceptance`, `completion-proof`, `new-target-reply`, `clarification-answer`, `corrected-artifact-response`, `none`, `unknown`)
- `created_at`

### Reply-stance receipt

A durable receipt proving that one imported reply was classified for stance/follow-up truth against one artifact family and one target scope.

Suggested fields:

- `reply_stance_receipt_id`
- `artifact_family_ref`
- `target_scope_ref`
- `ack_source_ref`
- `from_reply_stance`
- `to_reply_stance`
- `blocking_effect`
- `followup_class`
- `accepted_scope_ceiling`
- `supporting_refs[]`
- `created_at`

## Interface sections

Any client rendering imported reply meaning for one artifact family and one expected target should preserve this order:

1. **Object / scope / authorship companions**
2. **Current reply stance**
3. **Blocking or redirect effect**
4. **Smallest honest follow-up class**
5. **What stronger reply would change the verdict**
6. **Receipts and next honest action**

### 1) Object / scope / authorship companions

Show the current companion answers from `259`, `260`, and `261`:

- what exact object the reply appears to bind to
- who that reply can speak for
- whether the reply is machine-authored, mixed, or human-authored

This section answers:

**what kind of reply is this and what object/scope foundations does it already have?**

### 2) Current reply stance

Show one visible stance:

- `machine-operational-only`
- `acknowledges receipt`
- `acknowledges understanding`
- `requests clarification`
- `requests artifact change`
- `requests different channel or format`
- `redirects to different lane`
- `conditionally accepts pending step`
- `declines or rejects`
- `ambiguous`
- `unknown`

This section answers:

**what does the reply actually mean right now?**

### 3) Blocking or redirect effect

Show:

- whether the current claim remains non-blocking, follow-up-required, redirect-required, currently blocked, or terminally declined
- whether the present lane may still be used or whether the next honest move must happen through a different lane
- whether the current reply merely asked a question or actually rejected the request

This section exists because `human replied` is not enough to tell the operator whether anything can continue as-is.

### 4) Smallest honest follow-up class

Show one current follow-up class:

- `none`
- `answer clarification`
- `issue corrected artifact`
- `repackage or rechannel`
- `retarget lane`
- `provide stronger proof`
- `record decline and stop`
- `manual review`
- `unknown`

This section answers:

**what is the smallest honest next outward move now?**

### 5) What stronger reply would change the verdict

Show:

- whether explicit acceptance is still missing
- whether completion proof is required instead of more prose
- whether a new target or lane must reply before the stance can strengthen
- whether a corrected artifact must be issued and then acknowledged again

This section exists so the product does not merely say `not enough yet`; it says exactly what kind of stronger reply would matter.

### 6) Receipts and next honest action

Show:

- reply-stance receipts
- linked binding/scope/authorship receipts
- next honest action (`hold current claim`, `answer question`, `prepare corrected packet`, `retarget reviewed disclosure`, `record decline`, `other`)

## Rules

### Rule 1 — human reply is not automatic acceptance

A human-authored reply must not, by itself, prove that the current request was accepted.
A comment, question, or general acknowledgment may still leave follow-up required.

### Rule 2 — request-for-information is not rejection

A reply asking for more context, a better repro, fuller logs, or one narrower artifact should not be flattened into either `accepted` or `declined`.
It should remain a live follow-up-required stance with one explicit next move.

### Rule 3 — redirect is not acceptance by the new lane

If the current lane says `send this to security@...` or `use the portal instead`, that is a redirect.
It does not prove that the new lane already accepted, reviewed, or even received the artifact.

### Rule 4 — object exactness does not rescue missing stance

A reply may quote the exact correction notice or replacement artifact and still be only a clarification request or request-for-changes.
Exact binding may strengthen object truth, but it must not silently upgrade the stance to `accepted-current-request`.

### Rule 5 — audience scope does not rescue missing stance

A reply may come from the exact target lane or whole audience and still only request clarification, ask for a different format, or decline the request.
Scope truth and stance truth must remain separate answers.

### Rule 6 — machine-only operational replies remain weaker truths

Machine-only replies such as ticket creation, challenge-response, or automated routing hints may still create useful `machine-operational-only` or `redirect-required` truth.
They must not be discarded, but they also must not impersonate human semantic acceptance.

## CLI sketch

```text
anonsync ack stance show --family <artifact-family> --target <target>
anonsync ack stance import --family <artifact-family> --target <target> --from <source>
anonsync ack stance classify --ack <ack-source> --stance requests-clarification --followup answer-clarification
anonsync ack stance receipt show <receipt>
```

## Example states

- `Vendor replies: “Received. We understand the correction.”` → stance `acknowledges-understanding`, blocking effect `non-blocking`, follow-up `none` or `provide-stronger-proof` depending on the broader claim
- `Vendor replies: “Please attach one fuller route log and resend.”` → stance `requests-artifact-change`, blocking effect `follow-up-required`, follow-up `issue-corrected-artifact`
- `Vendor replies: “Please use security@vendor.example for this category.”` → stance `redirects-to-different-lane`, blocking effect `redirect-required`, follow-up `retarget-lane`
- `Human reply says “Looks good once the replacement packet includes the exact time window.”` → stance `conditionally-accepts-pending-step`, blocking effect `follow-up-required`, follow-up `issue-corrected-artifact`
- `Human reply says “We cannot review this request.”` → stance `declines-or-rejects`, blocking effect `terminal-decline`, follow-up `record-decline-and-stop`
- `Ticket system auto-create note arrives with no human text` → stance `machine-operational-only`, with object/scope/authorship companions still preserved separately

## Anti-goals

This spec does not:

- create a generic helpdesk or CRM product
- replace exact-object binding from `259`
- replace actor-scope and audience-ceiling truth from `260`
- replace human-proof and automation classification from `261`
- infer semantic refusal or acceptance from silence alone

## Companion surfaces

- `259-imported-recipient-acknowledgment-binding-exactness-and-claim-ceiling-interface-spec.md`
- `260-imported-acknowledgment-actor-scope-delegation-and-audience-ceiling-interface-spec.md`
- `261-imported-acknowledgment-authorship-automation-classification-and-human-proof-interface-spec.md`
- `245-external-blocker-handoff-followup-and-return-proof-interface-spec.md`
- `253-shareable-artifact-carryforward-delta-ledger-and-refresh-notice-interface-spec.md`
