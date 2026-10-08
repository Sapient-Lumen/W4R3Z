# Offer delivery-handoff provenance, preview authority, and app-intake boundary interface spec

## Purpose

The archive already separates:

- artifact lifetime from durable trust promotion
- sender intent from actual redeemer identity
- artifact budget from per-redemption trust fanout
- repeated-attempt equivalence from honest slot treatment
- predecessor/successor reissue lineage from raw link recreation

One real gap still remained:

> once a portable offer travels through a browser landing page, QR scanner, e-mail client, clipboard, or other delivery surface, the operator still needs one explicit answer to what was merely previewed in transit, what was actually ingested by the local app, what any external service could see, and what facts only became authoritative after local inspection.

This document turns that boundary into one explicit interface contract.
It is the delivery/handoff companion to `52-capability-offer-and-claim-artifact-spec.md`, the preview-truth companion to `66-claim-and-adoption-intake-interface-spec.md`, and the portable-offer companion to `113-offer-recipient-intent-and-redeemer-identity-boundary-interface-spec.md` through `116-offer-reissue-lineage-and-successor-boundary-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful but incomplete way.
`Link structure and flow` says a clicked Sync link first opens a landing page on the Resilio website that shows only basic folder info such as folder name and approximate size; if the browser has seen Sync links before, the page may immediately transfer the link into the Sync app; and the URL parameters after `#` are not actually sent to Resilio's server.
`Comprehensive guide to syncing (Desktop-Desktop)` says a link can be sent through e-mail or any convenient and trusted way, and that the default browser may ask permission to launch the external Sync application and may remember that choice.
Those docs are helpful, but they still leave one operator question too reconstructive:

- which delivery channel carried the artifact here
- what metadata was merely previewed outside the app
- whether any external surface saw only a wrapper URL, saw the full artifact, or only observed a landing-page hit
- whether the handoff into the local app was automatic, browser-confirmed, manual paste, QR scan, or local-file import
- which facts are merely delivery hints versus locally parsed artifact semantics versus fully authoritative, receipt-backed facts

That is not a criticism of browser links, QR codes, or landing pages.
It is a criticism of any surface that lets `the browser showed a folder name` or `the app auto-opened` stand in for one explicit proof story about delivery path, external touch, preview authority, and post-ingest truth.
AnonSync should therefore expose one explicit **delivery-handoff provenance and preview-authority contract** wherever portable offers cross surface boundaries before the real local inspection begins.

## Core rule

Delivery preview, artifact ingestion, and authoritative local inspection are three separate public facts.

A browser page, QR overlay, e-mail body, or clipboard preview may show something about an offer.
The local app may then ingest a portable artifact through a handoff step.
Only after local inspection and later review should the product claim authoritative offer semantics, trust consequences, or local-admission readiness.
None of those stages collapse the others.

The product is not fully inspectable until it can answer ten questions in one place:

1. which delivery channel carried the artifact here
2. which preview surface, if any, displayed metadata before local inspection
3. what metadata was shown there
4. what any external service or wrapper surface could actually observe
5. whether the handoff into the local app was automatic, confirmed, manual, or local-only
6. which fields were only preview hints
7. which fields were locally parsed from the received artifact
8. which fields are authoritative only after local inspection or later review
9. what tempting but unsafe shortcut is being refused
10. which receipt later proves the delivery path, preview-authority boundary, and current authoritative interpretation

If the operator still has to infer from `clicked in browser`, `opened automatically`, and a folder-name preview whether the artifact is already trusted, locally parsed, or externally disclosed, the surface is not explicit enough.

## Public objects

### Offer delivery-handoff row

A compact read object describing how one portable offer arrived, what was previewed before app ingestion, and what the current authority boundary is.

Suggested fields:

- `offer_delivery_handoff_row_id`
- `offer_ref` nullable
- `delivery_event_ref`
- `delivery_channel` (`browser-link-click`, `browser-auto-handoff`, `browser-confirmed-external-app`, `clipboard-paste`, `manual-text-entry`, `qr-scan`, `email-client-open`, `saved-file-open`, `api-submit`, `local-app-share`, `unknown`)
- `preview_surface` (`browser-landing-page`, `qr-overlay`, `mail-body`, `chat-message`, `file-manager`, `none`, `unknown`)
- `preview_fields[]` (`folder-name-hint`, `approx-size-hint`, `issuer-hint`, `expiry-hint`, `version-hint`, `none`, `unknown`)
- `external_touch_posture` (`local-only`, `wrapper-url-observed`, `landing-page-hit-fragment-not-sent`, `external-surface-saw-full-artifact`, `unknown`)
- `handoff_posture` (`auto-transferred-to-app`, `browser-confirmed-launch`, `manual-copy-into-app`, `local-file-import`, `local-only`, `blocked`, `unknown`)
- `preview_authority_posture` (`preview-only`, `artifact-derived-unreviewed`, `locally-parsed`, `locally-inspected`, `receipt-backed`, `unknown`)
- `authoritative_offer_ref` nullable
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Delivery-authority explanation

A read object explaining the exact boundary between delivery preview and authoritative local interpretation.

Suggested fields:

- `offer_delivery_authority_explanation_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `delivery_channel`
- `preview_surface`
- `external_touch_posture`
- `handoff_posture`
- `preview_authority_posture`
- `preview_summary`
- `authoritative_summary`
- `non_effect_summary`
- `why`
- `proof_refs[]`

### Delivery-handoff review plan

A prepared review object for deciding whether one delivery event may proceed to local inspection, needs stronger warning language, or should be reissued or re-delivered through a narrower channel.

Suggested fields:

- `offer_delivery_handoff_plan_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `current_delivery_channel`
- `current_external_touch_posture`
- `current_preview_authority_posture`
- `requested_outcome` (`continue-to-local-inspect`, `require-manual-confirm`, `freeze-at-preview-only`, `re-deliver-local-only`, `reissue-narrower-artifact`, `reject-ambiguous-handoff`, `keep-current-policy`)
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Delivery-handoff receipt

A durable object proving how one portable offer crossed a delivery surface, what was merely previewed there, and what became authoritative afterward.

Suggested fields:

- `offer_delivery_handoff_receipt_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `delivery_channel`
- `preview_surface`
- `preview_fields[]`
- `external_touch_posture`
- `handoff_posture`
- `preview_authority_posture_before`
- `preview_authority_posture_after`
- `authoritative_offer_ref` nullable
- `outcome`
- `recorded_at`
- `proof_refs[]`

## Delivery channel classes

### `browser-link-click`

Use when an operator clicked a portable link in a browser but the browser did not yet auto-transfer it into the local app.

### `browser-auto-handoff`

Use when a browser immediately transferred the link to the local app due to remembered protocol permission.
This class must render stronger reminder language because convenience can hide the handoff boundary.

### `browser-confirmed-external-app`

Use when a browser prompted the operator before launching the local app.

### `clipboard-paste`

Use when a portable offer string is pasted into the app or CLI directly.

### `manual-text-entry`

Use when the operator typed or otherwise re-entered offer material manually.

### `qr-scan`

Use when the delivery wrapper is a QR presentation rather than a text link.

### `saved-file-open`

Use when an offer artifact was opened from the local filesystem.

## Preview authority postures

### `preview-only`

Use when the surface is showing hints that the app has not yet parsed or verified locally.

### `artifact-derived-unreviewed`

Use when the app has the artifact bytes or text but has not yet completed normalized inspection.

### `locally-parsed`

Use when the app has parsed the artifact and can describe its declared semantics, but later review or contact proof may still narrow the truth.

### `locally-inspected`

Use when the local inspect step has completed and the artifact's own declared policy is authoritative for inspection purposes.

### `receipt-backed`

Use when later claim/review receipts now prove the delivery event and authoritative interpretation chain.

## External touch postures

### `local-only`

Use when the artifact never crossed an external preview surface before local inspection.

### `wrapper-url-observed`

Use when an external surface could observe a wrapper URL or transport shell, but not the full authority-bearing payload.

### `landing-page-hit-fragment-not-sent`

Use when a browser reached a landing page that rendered preview metadata while the authority-bearing fragment or payload was not transmitted to the landing-page service.

### `external-surface-saw-full-artifact`

Use when the channel actually exposed the full portable artifact to a third-party surface or service.
This class should render stronger review language.

## Fixed inspection order

Every delivery-handoff surface should preserve the same sections in the same order:

1. **Received via and external touch**
2. **What the preview surface actually showed**
3. **What the local app has parsed so far**
4. **What is authoritative now**
5. **What definitely is not implied**
6. **Receipts and proof links**

### 1) Received via and external touch

This section should show:

- delivery channel
- whether a browser/QR/mail/chat/file-manager surface was involved
- whether the external surface saw a wrapper only, landing-page hit only, or the full artifact
- whether the handoff into the local app was automatic, confirmed, manual, blocked, or local-only

### 2) What the preview surface actually showed

This section should show:

- preview surface class
- preview fields rendered there
- any clearly approximate or hint-only values
- whether the local app is merely restating those hints or has already parsed the actual artifact

### 3) What the local app has parsed so far

This section should show:

- normalized artifact ID if available
- declared subject, expiry, budget, or sender-intent posture if already parsed locally
- whether parsing happened through app inspect, CLI inspect, or deferred handoff
- any parse blockers or ambiguity

### 4) What is authoritative now

This section should show:

- preview-authority posture
- authoritative summary in one or two sentences
- whether later review is still required for admission, trust promotion, or claim application
- which receipt or inspect record currently grounds the answer

### 5) What definitely is not implied

This section should say, in plain language:

- previewed folder name or size does not prove trust or byte availability
- automatic browser handoff does not prove deliberate approval by the operator in this moment
- landing-page display does not mean the external service saw the full authority-bearing payload
- locally parsed artifact semantics do not yet prove later claim or remembered-trust consequences

### 6) Receipts and proof links

This section should link to:

- delivery-handoff receipt
- inspect receipt
- later claim or approval receipts if they exist
- predecessor or successor offer lineage when relevant

## Review grammar

Good labels:

- `Received via browser handoff`
- `Previewed in browser only`
- `Landing page saw wrapper; fragment stayed local`
- `Locally parsed after handoff`
- `Authoritative after inspect`
- `Full artifact exposed to external surface`
- `Re-deliver through local-only channel`

Bad labels:

- `Trusted link`
- `Verified in browser`
- `Safe because auto-opened`
- `Website approved`
- `Same as inspected`

## CLI implications

Example commands:

```text
anonsync offer intake show --latest
anonsync offer intake inspect dlv_01J...
anonsync offer inspect --from-browser-handoff dlv_01J...
anonsync offer handoff explain dlv_01J...
anonsync offer handoff review prepare dlv_01J... --outcome continue-to-local-inspect
anonsync offer handoff receipt show dhr_01J...
```

CLI output should keep `Received via`, `Preview said`, `Parsed locally`, `Authoritative now`, and `Not implied` adjacent.

## Daemon/API implications

A local daemon should expose delivery events separately from offer artifacts and claim outcomes.
Minimum surface:

```text
GET    /v1/offer-delivery-events
GET    /v1/offer-delivery-events/{delivery_event_id}
GET    /v1/offer-delivery-events/{delivery_event_id}/explain
POST   /v1/offer-delivery-events/{delivery_event_id}/inspect
POST   /v1/offer-delivery-events/{delivery_event_id}/prepare-review
GET    /v1/offer-delivery-handoff-receipts
GET    /v1/offer-delivery-handoff-receipts/{receipt_id}
```

Event stream additions:

- `offer.delivery_event_observed`
- `offer.delivery_preview_recorded`
- `offer.delivery_handoff_completed`
- `offer.delivery_authority_posture_changed`
- `offer.delivery_handoff_receipt_issued`

## Workbench implications

The workbench should add one intake-adjacent drawer or lane for **Received via / Preview / Parsed / Authoritative**.
That surface should let an operator answer, without opening logs:

- did this artifact come from browser auto-handoff, manual paste, QR scan, or local-only import
- what did the preview surface claim before the app inspected anything
- did any external service see only a wrapper or the full artifact
- what has the app parsed locally now
- what is still only hint-level, and what is actually authoritative

The workbench must not let `clicked in browser` become a trust badge.
Delivery convenience and preview confidence must remain inspectable public state.

## Canonical questions this layer must answer

A mature operator surface should be able to answer all of these without support-lore reconstruction:

- “Did this arrive through a browser landing page, clipboard, QR, or local file?”
- “What exactly was shown before the app inspected it?”
- “Did any third-party surface see the full artifact or only a wrapper?”
- “Was the handoff into the app automatic, confirmed, or manual?”
- “Which values are still hints, and which values are authoritative now?”
- “Which receipt proves that distinction later?”

## Non-clone conclusion

Resilio's current docs are useful precisely because they expose the seam.
They explain that a clicked link may open a landing page, may immediately hand off to the app, and may keep the authority-bearing fragment out of the landing-page request.
What they do not turn into one first-class operator surface is the boundary between `previewed outside the app` and `authoritative inside the app`.

AnonSync should keep the convenience while refusing the ambiguity.
The product should expose one explicit delivery-handoff provenance and preview-authority model so browser pages, QR overlays, clipboard strings, and local app inspection never blur into one vague `opened link` story.
