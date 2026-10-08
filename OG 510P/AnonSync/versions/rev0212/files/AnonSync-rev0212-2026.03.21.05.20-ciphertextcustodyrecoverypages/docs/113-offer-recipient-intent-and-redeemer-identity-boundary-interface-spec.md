# Offer recipient-intent, redeemer identity, and durable-trust boundary interface spec

## Purpose

The archive already separates portable offer artifacts from claims, portable-offer lifetime from durable trust promotion, and remembered approval from subject-level reuse policy.
One real gap still remained:

> after a portable offer is handed around, claimed, or approved, the operator still needs one explicit answer to who the offer was meant for, who actually redeemed it, whether any mismatch mattered, and what durable trust, if any, survived that real redemption.

This document turns that question into one explicit interface contract.
It is the recipient-intent companion to `52-capability-offer-and-claim-artifact-spec.md` and the redeemer/provenance companion to `112-offer-artifact-expiry-and-trust-promotion-boundary-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Sync Share Dialog (Desktop)` says a link may be copied to clipboard and pasted into messenger or e-mail, and that with approval disabled any peer who gets the link will connect automatically.
`Comprehensive guide to syncing (Desktop-Desktop)` says the key or link can be sent using any convenient and trusted way and the remote device adds the shared folder or clicks the link in a browser.
`Link structure and flow` then says the actual redeemer sends its locally generated public key, the approval dialog shows that redeemer's user name and fingerprint, and successful approval mints certificate-backed access and an ACL entry.

Taken together, those current docs imply a real operator question:

- the offer artifact can travel through ordinary channels
- the sender may still have had one *intended* recipient in mind
- the approval dialog identifies the *actual* requester who redeemed it
- successful redemption may mint durable trust that matters later
- nothing in that portable-offer story should silently answer whether the actual redeemer matched the sender's intent or whether any mismatch was accepted only for this subject versus promoted into broader remembered approval

That is not a criticism of portable links, QR codes, or certificate-backed approval.
It is a criticism of any surface that leaves the operator reconstructing whether the real redeemer was the intended recipient and whether a redeemed artifact should later count as durable trust for that redeemer.
AnonSync should therefore expose one explicit **offer recipient-intent, redeemer identity, and durable-trust boundary contract** wherever portable invitation artifacts and later approval reuse might otherwise blur together.

## Core rule

Sender intent, actual redeemer identity, and durable trust are three separate public facts.

An offer artifact may be portable and redeemable by whoever possesses it.
A sender may still record intended-recipient posture for that artifact.
A successful claim or approval may still create durable remembered approval.
None of those facts collapse the other two.

The product is not fully inspectable until it can answer seven questions in one place:

1. which offer artifact carried the authority
2. what recipient-intent posture the sender declared for that artifact
3. who actually redeemed or attempted to redeem it
4. how the actual redeemer relates to the stated intent (`match`, `family match`, `unexpected`, `forwarded`, `unknown`)
5. whether any mismatch was rejected, accepted only for this subject, accepted only for one reviewed seat, or promoted further
6. what tempting but unsafe shortcut is being refused
7. which receipts later prove the artifact, the real redeemer, the mismatch outcome, and any surviving durable trust

If the operator still has to infer from `copied link`, approval dialog history, and later remembered approval whether the offer was redeemed by the right identity and what trust survived that fact, the surface is not explicit enough.

## Public objects

### Offer recipient-intent row

A compact read object describing sender intent, actual redeemer identity, and what trust boundary survived after redemption.

Suggested fields:

- `offer_recipient_intent_row_id`
- `offer_ref`
- `seat_ref`
- `subject_ref`
- `recipient_intent_posture` (`portable-open`, `named-human-hint`, `subject-bound-human-hint`, `reviewed-seat-expected`, `family-expected`, `unknown`)
- `intended_recipient_label`
- `actual_redeemer_ref`
- `actual_redeemer_proof_basis` (`approval-request-fingerprint`, `claim-key-proof`, `linked-family-proof`, `human-confirmed`, `unknown`)
- `intent_match_class` (`matches-reviewed-seat`, `matches-expected-family`, `matches-human-hint-only`, `unexpected-redeemer`, `forwarded-redeemer`, `unknown`)
- `mismatch_outcome` (`not-applicable`, `pending-review`, `rejected`, `accepted-subject-only`, `accepted-reviewed-seat-only`, `promoted-broader`, `frozen-explanation-only`, `unknown`)
- `resulting_promotion_posture`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Offer redeemer explanation

A read object explaining who actually redeemed the artifact and what trust boundary that real redemption created.

Suggested fields:

- `offer_redeemer_explanation_id`
- `offer_ref`
- `subject_ref`
- `recipient_intent_posture`
- `intended_recipient_label`
- `actual_redeemer_ref`
- `actual_redeemer_proof_basis`
- `intent_match_class`
- `mismatch_outcome`
- `resulting_promotion_posture`
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Offer recipient-intent review plan

A prepared review object for one attempt to reject a mismatch, accept it only for the current subject, bind it to one reviewed seat, or promote it further.

Suggested fields:

- `offer_recipient_intent_plan_id`
- `offer_ref`
- `seat_ref`
- `subject_ref`
- `current_recipient_intent_posture`
- `current_actual_redeemer_ref`
- `current_intent_match_class`
- `requested_outcome` (`accept-as-expected`, `accept-subject-only`, `accept-reviewed-seat-only`, `reject-mismatch`, `reissue-for-named-recipient`, `freeze-explanation-only`, `require-fresh-human-confirmation`)
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Offer redeemer receipt

A durable object proving who actually redeemed the portable offer, how that compared to sender intent, and what trust outcome followed.

Suggested fields:

- `offer_redeemer_receipt_id`
- `offer_ref`
- `subject_ref`
- `intended_recipient_label`
- `actual_redeemer_ref`
- `actual_redeemer_proof_basis`
- `intent_match_class`
- `previous_mismatch_outcome`
- `outcome`
- `reviewed_at`
- `resulting_mismatch_outcome`
- `resulting_promotion_posture`
- `proof_refs[]`

## Recipient-intent postures

### `portable-open`

Use when the sender intentionally treats the artifact as redeemable by any holder and does not assert a narrower intended-recipient story.

### `named-human-hint`

Use when the sender records an intended human recipient label, but the product does not yet have a stronger reviewed seat binding for that label.

### `subject-bound-human-hint`

Use when the sender expects one human recipient for this governed subject, but the expectation is still weaker than a reviewed seat binding.

### `reviewed-seat-expected`

Use when the sender expects one specific reviewed seat or one cryptographically stable recipient identity.

### `family-expected`

Use when the sender intentionally expects one reviewed family/constellation rather than one single seat.

### `unknown`

Use when the product cannot honestly determine recipient intent posture.

## Intent-match classes

### `matches-reviewed-seat`

Use when the actual redeemer matches the one reviewed seat the sender expected.

### `matches-expected-family`

Use when the actual redeemer differs from one seat but still matches the declared reviewed family expectation.

### `matches-human-hint-only`

Use when the redeemer appears consistent with a weaker sender hint, but the evidence does not rise to reviewed-seat certainty.

### `unexpected-redeemer`

Use when the actual redeemer does not match the declared expected seat/family/human label.

### `forwarded-redeemer`

Use when the artifact appears to have been passed onward and the actual redeemer is not the originally expected party.

### `unknown`

Use when the product cannot make an honest match claim.

## Fixed inspection order

Every offer-recipient-intent surface should preserve the same sections in the same order:

1. **Offer artifact and sender intent**
2. **Actual redeemer and proof**
3. **Mismatch outcome and trust boundary**
4. **What definitely is not being claimed**
5. **Admissible reviewed outcomes**
6. **Receipts and proof links**

### 1) Offer artifact and sender intent

This section should show:

- which offer artifact is in view
- how it was delivered
- what recipient-intent posture the sender declared
- next honest action

The operator must be able to answer: **who did the sender mean this offer for, if anyone in particular?**

### 2) Actual redeemer and proof

This section should show:

- which identity actually redeemed or attempted to redeem the artifact
- the proof basis for that claim
- whether the redeemer arrived through approval review, direct claim proof, or later linked-family evidence
- whether the match is exact, family-level, hint-only, unexpected, forwarded, or unknown

The operator must be able to answer: **who actually redeemed it, on what proof?**

### 3) Mismatch outcome and trust boundary

This section should show:

- the mismatch outcome
- the resulting promotion posture
- whether the result stays subject only, reviewed-seat only, or broader
- whether later convenience is allowed, blocked, or explanation only

The operator must be able to answer: **did any mismatch matter, and what trust survived anyway?**

### 4) What definitely is not being claimed

This section should show:

- that a portable artifact being redeemable does not mean the sender intended every holder equally
- that successful approval does not prove the redeemer matched the sender's original intent
- that accepting an unexpected redeemer for one subject does not silently authorize later unrelated subjects
- that this review does not itself bind a path, materialize bytes, or widen reuse beyond the reviewed outcome

### 5) Admissible reviewed outcomes

This section should show only truthful verbs for the current posture, for example:

- `Accept as expected`
- `Accept for this subject only`
- `Accept for one reviewed seat`
- `Reject mismatch`
- `Reissue for named recipient`
- `Freeze to explanation only`
- `Require fresh human confirmation`

### 6) Receipts and proof links

This section should show:

- the original offer artifact receipt
- the claim or approval receipt proving who redeemed it
- any mismatch-review receipt
- any trust-promotion or trust-freeze receipt that followed

## Dense-row contract

Even dense/mobile surfaces must keep five things adjacent:

- recipient-intent posture
- actual redeemer
- match class
- resulting trust boundary
- next honest action

A truthful dense row is therefore closer to:

```text
Named for Mira   Redeemed by tablet-lapis   Unexpected redeemer   Subject only   Review mismatch
```

than to:

```text
Accepted   Approved before   Connected
```

## Non-clone conclusion

Resilio's current docs are strong enough to teach two useful lessons at once.
First, portable link/QR mechanics plus fingerprint-based approval review are genuinely useful.
Second, they still leave too much room for the operator to reconstruct whether the actual redeemer matched the sender's intent and what durable trust followed from that exact redemption.

AnonSync should keep the convenience while replacing the ambiguity.
The product should expose one explicit recipient-intent and redeemer-identity model so `for`, `redeemed by`, `accepted mismatch`, and `trust survived` remain inspectable public facts.
