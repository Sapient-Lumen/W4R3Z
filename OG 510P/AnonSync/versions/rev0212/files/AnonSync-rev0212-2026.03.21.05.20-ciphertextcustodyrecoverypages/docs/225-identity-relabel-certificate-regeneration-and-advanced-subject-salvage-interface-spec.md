# Identity relabel, certificate regeneration, and advanced-subject salvage interface spec

## Purpose

The archive already had subject-label continuity, successor cutover, compromise rotation, and seat replacement language.
What it still lacked was one tighter interface contract for the deceptively simple request:

> "I only want to rename this identity."

Current Resilio docs make this seam unusually sharp.
They still say the identity name participates in certificate generation, that there is no simple rename path, and that changing the name requires unlinking the current identity and generating a new certificate.
The same doc still says this removes Advanced folders from that Sync instance while Standard folders remain, and that other linked devices must be unlinked and linked again to the newly created identity.

That is not a harmless profile-label edit.
It is authority replacement with subject fallout.

AnonSync should not clone that shape.

## Core decision

AnonSync must never let a request to rename an identity silently collapse into authority replacement.

A user asking to rename a seat, person, or subject-visible identity must see one review that classifies the request as one of these:

- **label correction only**
- **peer-visible alias change with same authority**
- **same-person new-authority rotation**
- **seat replacement with salvage**
- **blocked because the operator actually needs successor / compromise / replacement flow**

The product should not make the user discover afterward that a spelling correction really meant `unlink, regenerate authority, and reattach sensitive subjects`.

## Why this matters

Current Resilio behavior still leaves three truths scattered across help pages instead of one reviewed surface:

- an identity display name is entangled with certificate creation
- changing the name is achieved by unlinking and creating a new identity
- Advanced-folder continuity does not survive that step on the current seat

AnonSync should instead hold one stronger rule:

> names are mutable labels; authority is a separate object; salvage plan comes before rotation.

## Fixed review order

Every non-trivial identity-relabel request should render the same sections in the same order:

1. **Requested label change**
2. **Current authority continuity**
3. **Subject and share fallout**
4. **Admissible outcomes**
5. **Receipt promise**

### 1) Requested label change

Show:

- current local label
- proposed new label
- audience (`local only`, `peer visible`, `constellation visible`, `artifact only`)
- whether the operator asked to preserve current authority
- whether a new authority is even being proposed

The operator must be able to answer:

> am I changing a label, or asking for a new authority story?

### 2) Current authority continuity

Show:

- current authority handle and issuance epoch
- seats currently bound to it
- trust memory attached to it
- whether approvals, grants, or peer trust records would survive a relabel
- whether the proposed action keeps or replaces that authority

Good status labels include:

- `label-only; authority unchanged`
- `new alias on existing authority`
- `new authority would be created`
- `authority replacement blocked pending salvage plan`

### 3) Subject and share fallout

Show:

- Advanced / high-governance subjects presently attached
- Standard / lower-governance subjects presently attached
- approvals or auto-approval memory that would stay or fall away
- linked seats that would require relink or review
- receipts that would remain searchable under old and new labels

The operator must be able to answer:

> what real continuity am I about to lose if I treat this as a rename?

### 4) Admissible outcomes

Primary actions should be explicit:

- `Change local label only`
- `Publish peer-visible alias`
- `Keep old label searchable as alias`
- `Open reviewed authority-rotation plan`
- `Open seat-replacement-and-salvage plan`
- `Block and explain why`

The product should not show a generic `Rename identity` button when the honest action is `Rotate authority and salvage subjects`.

### 5) Receipt promise

The resulting receipt must prove:

- whether any authority changed
- which labels changed and where they are visible
- which subjects stayed bound
- which seats must relink or review
- which old labels remain searchable

## Main surface

The identity/settings surface should show a split row:

- **Display label**
- **Authority handle**
- **Current aliases**
- **Bound seats**
- **Salvage-sensitive subjects**

Selecting `Change label` must open the review above, not a single text field that ambiguously edits both presentation and trust identity.

## Object model implications

### Identity relabel request

Fields:

- `identity_relabel_request_id`
- `authority_ref`
- `current_label`
- `proposed_label`
- `visibility_scope`
- `requested_continuity_mode` (`preserve-authority`, `new-authority`, `unspecified`)
- `acting_seat_ref`
- `status`

### Identity relabel review

Fields:

- `identity_relabel_review_id`
- `authority_ref`
- `request_ref`
- `continuity_class` (`label-only`, `alias-only`, `new-authority-rotation`, `seat-replacement`, `blocked`)
- `subject_fallout_refs[]`
- `seat_fallout_refs[]`
- `approval_memory_effect`
- `recommended_actions[]`
- `receipt_promise`

### Identity relabel receipt

Fields:

- `identity_relabel_receipt_id`
- `authority_ref_before`
- `authority_ref_after`
- `old_labels[]`
- `new_labels[]`
- `alias_records_created[]`
- `subject_effect_summary`
- `seat_effect_summary`
- `recorded_at`

## Explicit non-goals

AnonSync should not:

- regenerate authority because a user corrected capitalization or spelling
- silently discard governance-heavy subjects from a seat on rename
- make operators relink other seats without telling them that continuity changed
- treat old labels as disposable if they remain relevant for audit, search, or approvals

## Relationship to nearby specs

This spec is the specific relabel/salvage companion to:

- `84-subject-label-and-authority-identity-continuity-spec.md`
- `169-subject-kind-migration-and-capability-upgrade-review-interface-spec.md`
- `173-compromise-response-identity-rotation-and-stolen-seat-review-interface-spec.md`
- `202-identity-root-health-folder-list-salvage-and-relink-ladder-interface-spec.md`

Those documents already explain broader continuity and recovery doctrine.
This one fixes the operator-facing rename contract so a label edit cannot masquerade as ordinary profile hygiene.
