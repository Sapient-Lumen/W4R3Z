# Offer carrier-alias equivalence and canonical artifact identity interface spec

## Purpose

The archive already separates:

- sender intent from actual redeemer identity
- artifact budget from per-redemption trust fanout
- repeated-attempt equivalence from honest slot treatment
- successor-artifact lineage from raw reissue convenience
- delivery/handoff preview from authoritative local inspection

One real gap still remained:

> once the same portable offer can appear as a browser wrapper URL, browser landing-page handoff, `btsync://` protocol URL, copied link text, QR encoding, or later local file wrapper, the operator still needs one explicit answer to whether those things are the same artifact, a delivery-only alias, or a genuinely new successor.

This document turns that boundary into one explicit interface contract.
It is the canonical-identity companion to `52-capability-offer-and-claim-artifact-spec.md`, the carrier-side companion to `117-offer-delivery-handoff-provenance-and-preview-authority-boundary-interface-spec.md`, and the alias-equivalence companion to `115-offer-redemption-equivalence-and-slot-consumption-policy-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam real in a useful but incomplete way.
`Link structure and flow` says a Sync link uses an `https://link.resilio.com/...#...` wrapper, that the landing page may rewrite the scheme to `btsync://` so the Sync app can open it, and that the parameters after `#` are not sent to the Resilio server.
`Sync Share Dialog (Desktop)` says the same shared folder can be delivered as a link or QR code, while `Comprehensive guide to syncing (Desktop-Desktop)` says links may be copied to clipboard, sent by e-mail, or clicked in a browser.
Those docs are useful, but they still leave one operator question too reconstructive:

- whether wrapper URL, protocol rewrite, QR rendition, and copied text are one portable artifact or several
- whether a delivery-only re-encoding consumed fresh budget or started a new lineage branch
- whether a browser landing-page URL and an app-ingested protocol URL are aliases of the same authority-bearing payload
- whether a later file wrapper or alternate encoding is still the same offer, or instead a narrowed/broadened successor
- which receipts later prove that the product treated two different-looking carriers as one canonical artifact on purpose

That is not a criticism of multiple delivery carriers.
It is a criticism of any surface that lets carrier convenience masquerade as artifact identity.
AnonSync should therefore expose one explicit **carrier-alias equivalence and canonical artifact identity contract** wherever portable offers can travel through more than one encoding, wrapper, or handoff form.

## Core rule

Carrier form is not artifact identity.

A wrapper URL, protocol URL, QR payload, copied link string, local file envelope, or other transport shell may all represent the same portable offer.
Budget, trust consequence, successor lineage, and later audit should attach to the **canonical artifact identity**, not to whichever carrier happened to be seen last.

The product is not fully inspectable until it can answer eight questions in one place:

1. what the canonical artifact is
2. which carrier aliases are currently known for it
3. which carrier reached this seat now
4. whether that carrier is delivery-only, authority-bearing, truncated-preview, or ambiguous
5. which fields are identical across the alias family
6. which fields differ only because of encoding/wrapper behavior
7. whether anything about the current carrier forces `same artifact`, `new successor`, or `cannot prove equivalence yet`
8. which receipt later proves the alias judgment

If the operator still has to infer from `same folder name`, `same link`, browser history, or QR screenshots whether two carriers are actually the same artifact, the surface is not explicit enough.

## Public objects

### Offer carrier-alias row

A compact read object describing one known carrier of a portable artifact and its relationship to the canonical artifact identity.

Suggested fields:

- `offer_carrier_alias_row_id`
- `canonical_offer_ref` nullable
- `carrier_alias_ref`
- `carrier_kind` (`wrapper-url`, `protocol-url`, `qr-payload`, `clipboard-text`, `mail-body-copy`, `local-file-envelope`, `api-payload`, `manual-transcription`, `unknown`)
- `carrier_authority_posture` (`authority-bearing`, `delivery-wrapper`, `preview-only-copy`, `truncated`, `ambiguous`, `unknown`)
- `equivalence_posture` (`same-canonical-artifact`, `same-artifact-delivery-only-alias`, `same-artifact-authority-bearing-alias`, `successor-not-alias`, `cannot-prove-yet`, `unknown`)
- `normalization_basis[]`
- `alias_family_size`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Canonical artifact identity explanation

A read object explaining why several carriers do or do not collapse into one canonical artifact.

Suggested fields:

- `canonical_offer_identity_explanation_id`
- `canonical_offer_ref` nullable
- `candidate_carrier_alias_refs[]`
- `governing_equivalence_posture`
- `shared_semantic_fields[]`
- `carrier_only_fields[]`
- `delivery_only_differences[]`
- `successor_boundary_differences[]`
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Carrier-alias review plan

A prepared review object for deciding whether one newly observed carrier should collapse into an existing canonical artifact, remain pending, or fork into a successor lineage.

Suggested fields:

- `offer_carrier_alias_plan_id`
- `candidate_carrier_alias_ref`
- `comparison_canonical_offer_ref` nullable
- `current_equivalence_posture`
- `requested_outcome` (`collapse-into-canonical`, `record-delivery-only-alias`, `record-authority-bearing-alias`, `freeze-ambiguous-carrier`, `treat-as-successor`, `require-manual-compare`, `keep-current-policy`)
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Carrier-alias receipt

A durable object proving why one carrier was treated as an alias, wrapper-only copy, or new successor.

Suggested fields:

- `offer_carrier_alias_receipt_id`
- `canonical_offer_ref_before` nullable
- `canonical_offer_ref_after` nullable
- `carrier_alias_ref`
- `carrier_kind`
- `carrier_authority_posture`
- `equivalence_posture_before`
- `equivalence_posture_after`
- `normalization_basis[]`
- `outcome`
- `recorded_at`
- `proof_refs[]`

## Carrier classes

### `wrapper-url`

Use when the observed carrier is an outer delivery URL whose main purpose is browser landing, transport, or later rewrite into another scheme.

### `protocol-url`

Use when the observed carrier is the application-facing protocol form that the local app can ingest directly.

### `qr-payload`

Use when the artifact is encoded for optical delivery and may or may not exactly match another text representation.

### `clipboard-text` / `mail-body-copy`

Use when the same offer is carried as ordinary copied text rather than through a browser landing path.

### `local-file-envelope`

Use when an export/import wrapper stores the same offer in a local file or bundle.

## Carrier authority postures

### `authority-bearing`

Use when the carrier contains the full portable artifact needed for local parsing or claim preparation.

### `delivery-wrapper`

Use when the carrier is mainly a handoff shell or wrapper and the authority-bearing data is derived only after local normalization or fragment extraction.

### `preview-only-copy`

Use when the observed copy only shows hint metadata and is not itself sufficient for local claim preparation.

### `truncated`

Use when the carrier is visibly incomplete, redacted, or shortened such that canonical comparison is not yet trustworthy.

### `ambiguous`

Use when the product cannot yet prove whether the carrier holds the same full artifact or only an approximate wrapper.

## Equivalence rules

### Rule 1 — same semantic artifact, different wrapper, same canonical offer

If two carriers normalize to the same authority-bearing payload and no scope/policy/budget semantic changed, they must collapse into one canonical artifact even if the transport shells differ.

### Rule 2 — delivery-only re-encoding is not reissue

Changing only the delivery encoding — browser wrapper, QR rendering, copied text, file wrapper — must not silently create a new artifact family, new budget island, or new trust lineage.

### Rule 3 — successor semantics outrank carrier similarity

If expiry, scope, approval policy, intended recipient posture, or other governing semantics changed, the new thing is a successor even if its carrier looks nearly identical.

### Rule 4 — ambiguous carrier must stay ambiguous

A shortened message preview, screenshot of a QR code, or partial wrapper string must not be auto-collapsed into a canonical artifact merely because the folder hint looks familiar.

## Fixed inspection order

Every carrier-equivalence surface should preserve the same sections in the same order:

1. **Canonical artifact now**
2. **Carrier observed here**
3. **Other known aliases**
4. **Why these are the same or not the same**
5. **What definitely did not change**
6. **Receipts and proof links**

### 1) Canonical artifact now

This section should show:

- canonical offer reference when known
- current equivalence posture
- whether the current carrier collapsed into an existing artifact or remains pending

### 2) Carrier observed here

This section should show:

- carrier kind
- carrier authority posture
- delivery event reference if one exists
- which exact alias reached this seat now

### 3) Other known aliases

This section should show:

- wrapper URL aliases
- protocol URL aliases
- QR or file envelope aliases
- which aliases are authority-bearing versus delivery-only

### 4) Why these are the same or not the same

This section should show:

- normalization basis
- shared semantic fields
- carrier-only differences
- any blocker preventing automatic collapse

### 5) What definitely did not change

This section should show non-effects such as:

- a delivery-only alias did not mint new budget
- a QR rendering did not create a successor
- a browser wrapper did not become the authoritative artifact identity by itself

## Worked example

A clean review example:

- Alice creates one portable offer for `Research Photos`
- the app renders three carriers for the same offer: copied wrapper link, QR encoding, and local protocol handoff
- Ben first sees the wrapper in browser, then later pastes the protocol URL into another seat

Expected surface:

- one canonical offer row
- three carrier alias rows
- wrapper URL marked `delivery-wrapper`
- protocol URL marked `authority-bearing`
- QR marked either `authority-bearing` or `delivery-wrapper` depending on payload design
- no extra budget or successor lineage created merely because several carriers were seen

If Alice later narrows expiry or changes reuse policy and issues a new offer, that later carrier must show `successor-not-alias` even if its wrapper shape looks nearly identical.

## Non-clone conclusion

Resilio's current docs still teach two useful lessons at once.
First, it is genuinely useful to let one share travel through several convenient carriers: browser wrapper, protocol rewrite, QR, copied link, ordinary e-mail/message delivery.
Second, it is still too easy there for the human to reconstruct from carrier form what is actually one artifact.

AnonSync should keep the convenience while replacing the ambiguity.
The product should expose one canonical artifact identity, one carrier-alias ledger, explicit equivalence postures, and durable receipts proving whether two different-looking carriers were really the same offer or a later successor.
