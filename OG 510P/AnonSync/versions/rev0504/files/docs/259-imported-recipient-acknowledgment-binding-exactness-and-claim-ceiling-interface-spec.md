# Imported recipient acknowledgment binding, exactness, and claim-ceiling interface spec

## Problem it solves

AnonSync already distinguishes:

- local channel completion from stronger delivery witness
- current shareable head from current issued head
- correction notice from replacement issue
- recipient retarget from basis drift

What it still did not say cleanly was:

> once some outside reply, ticket comment, mailbox response, or imported acknowledgment arrives, **what exact thing did that acknowledgment bind to**?

A same-thread reply, generic "got it", delivery/read receipt, or copied acknowledgment blob should not silently impersonate:

- acknowledgment of one exact issued artifact
- acknowledgment of one exact correction notice
- acknowledgment that the recipient now interprets one older artifact as superseded
- acknowledgment that the newer replacement artifact is the thing currently understood as authoritative

This document defines one explicit **recipient-acknowledgment binding** object so AnonSync can preserve thread continuity, quoted/exact binding, and honest claim ceilings separately.

Actor scope is a separate seam; `260-imported-acknowledgment-actor-scope-delegation-and-audience-ceiling-interface-spec.md` answers who that reply can honestly speak for.

## Why this deserves first-class treatment

The comparison pressure that made this worth stealing came from two places:

- **DeriveBSD** reinforced that recipient hints, audience hints, and binding evidence should stay **lane-exact** instead of drifting across similar-looking but materially different scopes
- AnonSync's own newer disclosure / correction / issued-head work made the missing seam obvious: imported acknowledgment was becoming stronger, but the archive still lacked one explicit answer to `what exactly did the recipient acknowledge?`

## Core doctrine

For imported recipient acknowledgments, **thread continuity is not exact binding**.

A reply may prove that some recipient reacted in the same conversational lane.
It does not, by itself, prove which exact artifact, correction notice, or replacement the recipient meant.

AnonSync should therefore preserve at least these distinct answers:

1. what acknowledgment evidence arrived
2. which target or audience it came from
3. whether it is only same-thread / same-ticket / same-conversation continuity
4. whether it binds to an exact older issued artifact, exact correction notice, or exact replacement artifact
5. what the strongest honest claim ceiling is now
6. what stronger exactness proof would upgrade that ceiling

If `recipient acknowledged` still has to impersonate `recipient acknowledged this exact replacement/correction object`, the interface is not honest enough.

## Objects

### Recipient-acknowledgment binding row

A compact row classifying one imported recipient acknowledgment against one artifact family and one target scope.

Suggested fields:

- `recipient_ack_binding_row_id`
- `artifact_family_ref`
- `target_scope_ref`
- `ack_source_ref`
- `ack_channel_kind` (`email-reply`, `ticket-comment`, `same-product-redeem`, `chat-message`, `manual-attestation`, `api-callback`, `other`)
- `sender_match_verdict` (`exact-target`, `target-equivalent`, `same-domain-ambiguous`, `mismatch`, `unknown`)
- `conversation_continuity` (`same-thread`, `same-ticket`, `same-conversation`, `no-thread-proof`, `unknown`)
- `acknowledged_object_kind` (`none-exact`, `older-issued-artifact`, `correction-notice`, `replacement-artifact`, `refresh-notice`, `artifact-family-generic`, `ambiguous`, `unknown`)
- `binding_evidence_kind` (`generic-reply`, `thread-link-only`, `quoted-title-or-subject`, `quoted-snippet`, `explicit-artifact-id`, `exact-digest`, `same-product-successor-observed`, `operator-classified`, `unknown`)
- `binding_exactness` (`generic-only`, `family-only`, `object-probable`, `object-exact`, `same-product-exact`, `ambiguous`, `unknown`)
- `claim_ceiling` (`recipient-responded`, `recipient-ack-family-only`, `recipient-ack-object-probable`, `recipient-ack-object-exact`, `same-product-successor-exact`, `unknown`)
- `stronger_proof_needed` (`exact-quoted-object`, `artifact-id-match`, `digest-match`, `same-product-redeem`, `explicit-supersession-language`, `none`, `unknown`)
- `created_at`

### Acknowledgment binding receipt

A durable receipt proving that one imported acknowledgment was classified against one family / target scope with one exactness ceiling.

Suggested fields:

- `ack_binding_receipt_id`
- `artifact_family_ref`
- `target_scope_ref`
- `ack_source_ref`
- `from_claim_ceiling`
- `to_claim_ceiling`
- `acknowledged_object_kind`
- `binding_exactness`
- `supporting_refs[]`
- `created_at`

## Interface sections

Any client rendering imported acknowledgment truth for one artifact family and one target should preserve this order:

1. **Source acknowledgment and sender match**
2. **Conversation continuity**
3. **Exact object binding**
4. **Current claim ceiling**
5. **Stronger proof boundary**
6. **Receipts and next honest action**

### 1) Source acknowledgment and sender match

Show:

- where the acknowledgment came from
- whether the sender matches the expected target exactly, by proved equivalence, only loosely, or not at all
- whether this is a machine-generated receipt, a human reply, or a same-product successor observation

This section answers: **who answered, in what lane, and how exact is the sender match?**

### 2) Conversation continuity

Show:

- whether the imported evidence belongs to the same email thread, support ticket, or same-product redemption lane
- whether continuity exists only by mailbox/thread/ticket linkage
- whether continuity is absent and the acknowledgment was attached manually

This section exists because same-thread continuity is useful evidence, but it is weaker than exact object binding.

### 3) Exact object binding

Show:

- whether the acknowledgment points only to the artifact family in general
- whether it appears to acknowledge the older issued artifact
- whether it explicitly acknowledges the correction notice
- whether it explicitly acknowledges the replacement artifact
- what evidence created that binding (quoted title, quoted snippet, artifact id, digest, same-product successor, manual classification)

This section must answer: **what exact thing, if any, did the recipient acknowledge?**

### 4) Current claim ceiling

Show one visible ceiling:

- `recipient responded`
- `recipient acknowledged family only`
- `recipient acknowledged likely object`
- `recipient acknowledged exact object`
- `same-product successor exact`
- `unknown`

This ceiling may strengthen delivery or correction truth, but only up to the exactness actually proved.

### 5) Stronger proof boundary

Show the next stronger proof that would justify upgrading the ceiling, such as:

- explicit correction-notice quote
- exact replacement artifact id or digest
- same-product successor redemption
- explicit language that the older artifact should no longer be relied on

### 6) Receipts and next honest action

Show:

- acknowledgment-binding receipts
- linked outbound execution or correction-transition receipts
- linked issued-head or current-surface rows
- next honest action (`keep family-only ceiling`, `import better evidence`, `classify exact object`, `open ambiguity review`, `other`)

## Rules

### Rule 1 — same-thread is not same-object

An email or ticket reply in the same thread may prove conversational continuity.
It must not, by itself, prove that the recipient acknowledged one exact artifact, one exact correction notice, or one exact replacement artifact.

### Rule 2 — generic reply text is weaker than explicit supersession language

`thanks`, `got it`, `will review`, or similar generic responses may justify `recipient responded`.
They must not automatically justify `recipient acknowledged exact replacement` or `recipient understands the older artifact as superseded`.

### Rule 3 — read/delivery receipts are not semantic acknowledgment

A delivery receipt, read receipt, or mailbox-open signal may strengthen transport truth.
It must not be allowed to impersonate explicit acknowledgment of one exact object or supersession meaning.

### Rule 4 — same-product successor observation is stronger than message-thread folklore

If the product later observes one exact successor redemption or same-product apply event that is cryptographically or structurally tied to one replacement artifact, that witness may raise exactness above generic conversational acknowledgment.

### Rule 5 — exactness upgrades should name the object kind

Whenever the ceiling rises above `family-only`, the product must name which object kind became exact or probable:

- older issued artifact
- correction notice
- replacement artifact
- refresh notice

### Rule 6 — ambiguity should survive import honestly

If one reply could plausibly refer to the older issued artifact, the correction notice, or the replacement artifact, the surface should stay `ambiguous` until better evidence or explicit manual classification resolves it.

## CLI sketch

```text
anonsync ack show --family <artifact-family> --target <target>
anonsync ack import --family <artifact-family> --target <target> --from <source>
anonsync ack classify --ack <ack-source> --bind correction-notice:<id>
anonsync ack receipt show <receipt>
```

## Example states

- `Vendor replies "received" in the same email thread with no quote` → continuity `same-thread`, binding exactness `family-only` or `generic-only`, claim ceiling `recipient responded`
- `Vendor replies quoting the correction notice summary exactly` → acknowledged object `correction-notice`, binding exactness `object-probable` or `object-exact` depending on the quote, stronger correction ceiling allowed
- `Recipient redeems the replacement artifact through same-product successor flow` → acknowledged object `replacement-artifact`, binding exactness `same-product-exact`, strongest ceiling
- `Mailbox auto-responder returns a delivery/read signal` → transport witness may strengthen channel truth, but acknowledgment exactness remains weak or none

## Anti-goals

This spec does not:

- create a generic CRM or helpdesk system
- infer semantic acknowledgment from thread shape alone
- let read/open telemetry rewrite correction meaning silently
- replace the existing delivery witness, issued-head, or correction-register surfaces

## Companion surfaces

- `261-imported-acknowledgment-authorship-automation-classification-and-human-proof-interface-spec.md`

- `252-outbound-channel-execution-delivery-witness-and-claim-ceiling-interface-spec.md`
- `256-reviewed-recipient-target-guard-retarget-stale-and-reissue-interface-spec.md`
- `257-shareable-artifact-disclosure-queue-issued-head-and-current-surface-interface-spec.md`
- `258-issued-artifact-correction-notice-supersession-and-residual-reliance-interface-spec.md`
- `260-imported-acknowledgment-actor-scope-delegation-and-audience-ceiling-interface-spec.md`
- `263-imported-reply-referent-slice-quote-scope-and-request-coverage-interface-spec.md`
