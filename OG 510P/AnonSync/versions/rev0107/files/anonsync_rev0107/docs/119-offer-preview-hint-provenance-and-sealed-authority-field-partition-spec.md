# Offer preview-hint provenance and sealed-authority field partition spec

## Purpose

The archive already separates:

- delivery provenance from authoritative local inspection
- carrier alias equivalence from canonical artifact identity
- artifact budget from per-redemption trust consequence
- recipient intent from actual redeemer identity
- successor lineage from delivery-only re-encoding

One real gap still remained:

> even after the product can say `this browser wrapper, QR, and protocol URL are the same offer`, the operator still needs one explicit answer to which facts were merely preview hints, which facts stayed sealed until local parse, and which later actions may or may not rely on those different field classes.

This document turns that boundary into one explicit interface contract.
It is the field-provenance companion to `117-offer-delivery-handoff-provenance-and-preview-authority-boundary-interface-spec.md`, the exposure-clarity companion to `118-offer-carrier-alias-equivalence-and-canonical-artifact-identity-spec.md`, and the offer-field companion to `52-capability-offer-and-claim-artifact-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam real in a useful but incomplete way.
`Link structure and flow` says a clicked Sync link opens a landing page that shows basic folder info such as folder name and size, may rewrite `https://` to `btsync://` for the app, and keeps the parameters after `#` out of the request to the Resilio server.
The same article also says the link contains only the minimum information needed to start sync, including the folder identifier, temporary key, expiration, and producing-client version.
`Sync Share Dialog (Desktop)` and the quick guides still say the same share can be delivered as link, QR, or copied text through ordinary communication channels.
Those docs are useful, but they still leave one operator question too reconstructive:

- which facts were shown merely as human-facing hints before authoritative parse
- which fields remained sealed inside the authority-bearing payload until local ingestion
- which carrier-specific fields were only delivery mechanics rather than governed semantics
- whether a previewed name/size pair is enough to justify any later trust, budget, or claim inference
- which receipt later proves exactly what was visible, where, and with what authority class

That is not a criticism of preview hints.
It is a criticism of any surface that lets preview hints masquerade as authoritative offer truth.
AnonSync should therefore expose one explicit **preview-hint provenance and sealed-authority field partition contract** wherever portable offers can cross browser wrappers, QR renderings, copied text, protocol handoff, or later file-envelope forms.

## Core rule

A portable-offer field must always have both a **semantic role** and an **authority/exposure posture**.

Human hints such as folder label or approximate size may be shown before local parse without becoming authoritative claim/trust/budget truth.
Authority-bearing fields may remain sealed until local parse without becoming mysterious or folkloric.
Delivery-wrapper mechanics may vary without silently changing governed semantics.

The product is not fully inspectable until it can answer eight questions in one place:

1. which fields were shown before authoritative local inspection
2. which fields were only delivery/routing mechanics
3. which fields remained sealed until local parse
4. which fields became authoritative only after local parse
5. which fields are relevant to later claim/trust/budget decisions
6. which fields are explicitly *not* enough for those later decisions
7. whether several carriers preserved the same field semantics under different exposure classes
8. which receipt later proves that field partition

If the operator still has to infer from browser chrome, QR screenshots, or remembered app-launch behavior whether a field was just a hint or a real authority-bearing input, the surface is not explicit enough.

## Public objects

### Offer field provenance row

A compact read object describing one offer field, what it means, and how/when it was exposed.

Suggested fields:

- `offer_field_provenance_row_id`
- `canonical_offer_ref` nullable
- `carrier_alias_ref` nullable
- `field_name`
- `field_semantic_role` (`human-hint`, `artifact-identity`, `delivery-routing`, `authority-bearer`, `policy-control`, `integrity-proof`, `telemetry-only`, `unknown`)
- `field_exposure_posture` (`preview-visible`, `carrier-visible-local-only`, `sealed-unparsed`, `locally-parsed-authoritative`, `delivery-wrapper-only`, `redacted`, `unknown`)
- `field_authority_posture` (`hint-only`, `supporting-but-not-sufficient`, `authoritative-after-parse`, `authority-bearing-but-not-yet-parsed`, `non-governing`, `unknown`)
- `seen_on_surfaces[]`
- `eligible_for_later_inference[]`
- `ineligible_for_later_inference[]`
- `supporting_receipt_refs[]`

### Offer field partition explanation

A read object explaining why some fields count as preview hints, why others stayed sealed, and which later actions can honestly rely on which classes.

Suggested fields:

- `offer_field_partition_explanation_id`
- `canonical_offer_ref` nullable
- `carrier_alias_refs[]`
- `preview_visible_fields[]`
- `sealed_until_local_parse_fields[]`
- `delivery_wrapper_only_fields[]`
- `authoritative_after_parse_fields[]`
- `later_claim_relevant_fields[]`
- `later_claim_irrelevant_fields[]`
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Offer field partition review plan

A prepared review object for deciding whether the current product surface is compressing preview hints and authoritative fields too aggressively.

Suggested fields:

- `offer_field_partition_plan_id`
- `candidate_offer_ref` nullable
- `current_partition_posture`
- `requested_outcome` (`expand-preview-hints`, `mark-hint-only`, `mark-sealed-until-parse`, `promote-authoritative-after-parse`, `freeze-ambiguous-field`, `require-local-inspect`, `keep-current-policy`)
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Offer field partition receipt

A durable object proving what field classes were visible where and with what authority posture.

Suggested fields:

- `offer_field_partition_receipt_id`
- `canonical_offer_ref` nullable
- `carrier_alias_ref` nullable
- `preview_visible_fields[]`
- `sealed_fields[]`
- `authoritative_after_parse_fields[]`
- `delivery_wrapper_only_fields[]`
- `outcome`
- `recorded_at`
- `proof_refs[]`

## Field semantic roles

### `human-hint`

Use for facts that help an operator recognize what they are looking at without by themselves authorizing trust, claim, or budget inferences.
Typical examples include folder label or approximate size when shown as landing-page or QR-adjacent hints.

### `artifact-identity`

Use for fields that help determine canonical-offer identity and alias equivalence.
These can matter deeply without all being preview-visible.

### `delivery-routing`

Use for wrapper/protocol/file-envelope mechanics that explain *how* the artifact moved, not *what governed subject* it represents.

### `authority-bearer`

Use for fields that actually enable local parse or later authority/claim preparation once the product ingests them.

### `policy-control`

Use for fields that influence expiry, approval requirements, intended-recipient constraints, or related governance.

## Exposure and authority rules

### Rule 1 — preview hint is not authority proof

A field shown on a landing page, QR caption, mail preview, clipboard preview, or chat snippet must not by itself justify trust, claim, budget, or successor inference unless the product can separately prove that the field is authoritative for that decision.

### Rule 2 — sealed fields must still be explainable

If a field remained sealed until local parse, the product should say that explicitly rather than making the operator guess whether the field was absent, hidden, or simply not yet inspected.

### Rule 3 — same offer may have different exposure postures across carriers

The same canonical artifact may appear through one carrier that previews only hints and another carrier that is fully authority-bearing.
That difference must not fork canonical identity, but it must remain visible as field-partition truth.

### Rule 4 — alias collapse does not collapse exposure history

Treating two carriers as the same canonical artifact must not erase which fields were preview-visible on one path, sealed on another, or authoritatively parsed only later.

### Rule 5 — field partition must name explicit non-effects

A field-partition surface should explicitly say things like:

- previewed folder label did not prove intended recipient match
- previewed size did not prove byte availability now
- sealed temporary authority material was not exposed on the landing request
- authoritative local parse still did not itself prove later approval or durable trust promotion

## Fixed inspection order

Every field-partition surface should preserve the same sections in the same order:

1. **Preview-visible hints**
2. **Sealed until local parse**
3. **Authoritative after local parse**
4. **What later actions may rely on which fields**
5. **What definitely may not be inferred**
6. **Receipts and proof links**

### 1) Preview-visible hints

This section should show:

- which fields were visible before local parse
- on which surfaces they were visible
- whether those fields were only recognition hints or supporting evidence

### 2) Sealed until local parse

This section should show:

- which fields stayed sealed prior to local inspection
- whether they were authority-bearing, policy-bearing, or integrity-related
- whether the current client has now parsed them or still has not

### 3) Authoritative after local parse

This section should show:

- which fields became authoritative only after local parsing
- whether those fields now support alias collapse, claim prep, or approval review
- what further review is still required before those later actions happen

### 4) Later-action reliance

This section should show:

- claim-relevant fields
- trust-relevant fields
- budget-relevant fields
- explicit sufficiency thresholds where one field alone is not enough

### 5) Explicit non-inference list

This section should show:

- what a browser/QR/mail preview did *not* prove
- what local parse still did *not* prove
- what stayed carrier-only mechanics rather than governed semantics

### 6) Receipts and proof links

This section should show:

- delivery-event receipts
- carrier-alias receipts
- field-partition receipts
- later claim or approval receipts only when actually relevant

## Cross-surface rules

### CLI

The CLI should support concise but honest projections such as:

- `Preview hints: name, approx-size`
- `Sealed until local parse: authority token, expiry, artifact id`
- `Authoritative now: artifact id, policy fields`
- `Not enough yet: no claim/trust inference from preview alone`

### Workbench

Dense rows should preserve at least:

- one `Preview hints` chip
- one `Sealed fields` chip
- one `Authoritative now` chip
- one `Not enough yet` chip or drawer link when any user could otherwise over-read the preview

### API

The daemon/API must let lightweight clients retrieve field-partition truth without forcing raw-log inspection or private parsing lore.

## Example judgments

### Example A — browser landing page plus app parse

Honest answer:

- preview-visible hints: folder label, approximate size
- sealed until parse: authority-bearing payload fields
- authoritative after local parse: canonical artifact id, policy-bearing fields
- non-inference: preview did not prove approval, byte availability, or recipient match

### Example B — QR screenshot without local scan

Honest answer:

- preview-visible hint: maybe folder label if printed alongside QR
- sealed fields: QR payload still unparsed
- authoritative now: none yet
- next safe action: local inspect or manual compare

### Example C — copied protocol URL pasted into app

Honest answer:

- preview-visible hints: maybe none beyond raw string shape
- sealed until parse: not applicable if the app has already parsed it immediately
- authoritative after local parse: canonical artifact id and governed fields
- non-inference: successful parse still did not itself prove later approval/trust outcomes

## What this changes elsewhere in the archive

This spec requires the rest of the archive to become stricter in five ways:

1. delivery provenance must keep field-level preview truth adjacent to authority truth
2. carrier alias collapse must preserve field-exposure history rather than erase it
3. offer-artifact objects must classify fields by semantic role and exposure posture
4. workbench rows must expose at least one compact `hint vs sealed vs authoritative` strip
5. the non-clone case against Resilio should now be stated precisely: the remaining issue is not that it previews folder hints or keeps the `#` fragment local — those are good ideas — but that the field-level authority boundary still is not one first-class public contract

## Acceptance test

The archive has absorbed this spec when all of the following are true:

- a portable-offer detail surface can distinguish preview-visible hints from sealed authority-bearing fields without debug-log archaeology
- the same canonical artifact can preserve different field-exposure histories across browser, QR, protocol, or file-envelope carriers
- a user cannot honestly claim `the landing page already proved it` when only hint fields were visible
- a user also cannot honestly claim `the hidden fields are mysterious` because the product explicitly names what stayed sealed and why
- a later claim, trust, or budget decision can cite the exact field classes it relied on and the receipt that proved them
