# Constrained-seat path consent, removable storage, and capability floor interface spec

## Purpose

The archive already had arrival-placement, path-comparison, capture-ingest, storage-pressure, and seat-switch language.
What it still lacked was one explicit interface contract for a very common but semantically messy class of device:

> a phone or otherwise constrained seat where accepting a share, choosing where it lands, deciding whether it may touch removable storage, and understanding which retention/recovery promises still hold are all meaningfully different actions.

Current official Resilio docs make this seam sharper than a generic `mobile is limited` shrug.
They still say Android `Simple Mode` puts all new shares in `Downloads/Sync` on internal storage, silently creates `(1)` duplicates on collision, and hides `Root directory` and `ExternalSD` from the picker.
They also still say that to pick a location during QR-based intake you must disable Simple Mode **before** scanning, that received single-file transfers go to `Downloads/SyncDownloads` on internal memory and that this path currently cannot be changed, that SD-card write access requires a separate root-level provider grant, that some backup flows can only target an existing SD-card folder, and that Archive does not work for Android shares located on SD cards.

That is all operationally real.
It is still not a good acceptance contract.
Path choice, storage consent, capability ceilings, and later recovery promises should not be hidden inside platform folklore.

## Core decision

AnonSync should treat every seat as publishing a visible **capability floor** and every incoming bind as requiring explicit **storage consent**.

Accepting a subject on a constrained seat must therefore be decomposed into four separate truths:

- `may this seat store this subject at all?`
- `which storage classes are available here?`
- `which class did the operator actually consent to use?`
- `which share semantics degrade because of that class?`

The product must never imply that `accepted here` means `full desktop-grade bind with unchanged retention/recovery semantics` unless that is actually true.

## Why this matters

Current Resilio docs still reveal six interface mistakes AnonSync should not clone:

- a convenience mode still changes the default landing root, hides alternative roots, and manufactures `(1)` suffixed duplicates without one intake review
- path choice for QR intake can still depend on disabling a setting **before** the claim flow begins
- removable-storage authorization is still distinct from path choice, yet the operator can learn that only after an attempted bind fails
- some paths can store bytes but not support the same retention/recovery features as internal storage
- single-file receipt can still use a fixed internal path that is not configurable from the receipt flow
- constrained backup/storage flows can still require an already-existing target folder, which means `create new` is not universally true even when the UI sounds like ordinary folder choice

AnonSync should therefore keep one stronger rule:

> storage class must be reviewed as part of acceptance, not discovered later through missing actions or repair pages.

## Fixed review order

Every constrained-seat bind should render the same sections in the same order:

1. **Seat capability now**
2. **Destination consent**
3. **Capability ceilings and degraded promises**
4. **Receipt and future posture**

### 1) Seat capability now

This section should show:

- seat type and runtime posture
- available storage classes:
  - sandbox/internal
  - removable/provider-granted
  - existing-folder-only
  - immutable receipt inbox
  - unavailable
- whether background execution exists
- whether archive/history, selective eviction, and restore are supported for the chosen class
- whether the seat can create a new folder or only choose an existing one

The operator must be able to answer: **what kinds of storage can this seat honestly use right now?**

### 2) Destination consent

This section should show:

- proposed destination root
- why it is being suggested
- whether this is an ordinary subject bind, a single-file receipt inbox, or a capture-only sink
- whether the root was chosen by the operator, inherited from a seat default, or forced by the platform
- duplicate-risk or suffix-risk if the destination already contains a similarly named subject

The operator must be able to answer: **where will this land, and did I actually choose that?**

### 3) Capability ceilings and degraded promises

This section should show:

- archive/history support
- restore support
- background-transfer posture
- whether deletion/eviction semantics differ from desktop seats
- whether the seat may only materialize on demand
- whether local editing/export flows will use imported copies instead of in-place mutation

The operator must be able to answer: **what becomes weaker because I chose this seat and this storage class?**

### 4) Receipt and future posture

This section should show:

- seat/storage class chosen
- bind root chosen
- any capability ceilings acknowledged
- whether this choice affects only this subject or changes future arrival defaults
- proof that storage access was granted or intentionally withheld

The operator must be able to answer: **what exactly did I allow this seat to do, and did it change future behavior?**

## Main surface

The intake sheet for a constrained seat should never collapse to one `Choose folder` line.
It should show a compact but explicit capability row such as:

- `internal sandbox only`
- `removable storage available after provider grant`
- `existing folder required on removable storage`
- `archive unsupported on this storage class`
- `single-file receipts use fixed inbox unless changed in settings`

If the product still expects the operator to remember which special storage classes disable which later actions, the acceptance model is not good enough.

## Object model implications

AnonSync should add or strengthen these objects:

- `seat_capability_floor`
- `storage_class_admission`
- `seat_destination_consent_review`
- `degraded_promise_notice`
- `seat_storage_receipt`

Suggested fields for `seat_capability_floor`:

- `seat_id`
- `storage_classes[]`
- `background_support`
- `create_new_folder_support`
- `archive_support_by_class{}`
- `restore_support_by_class{}`
- `forced_inbox_paths[]`
- `provider_grants[]`

## Event language

Use explicit phrases such as:

- `seat accepted subject on internal sandbox`
- `removable storage requires provider grant`
- `archive unavailable on chosen storage class`
- `receipt inbox path is platform-fixed`
- `existing-folder-only target required`
- `future arrival default unchanged`

Avoid vague lines such as:

- `mobile limitations apply`
- `folder created successfully`
- `storage selected`

## CLI shape

Example commands:

```text
anonsync seat capability <seat>
anonsync seat bind review --seat <seat> --subject <subject>
anonsync seat bind review --seat <seat> --storage-class removable --target <path>
anonsync seat receipt explain <receipt>
```

The CLI must show the same capability ceilings and consent facts as the local web UI.

## Failure and edge cases

### Seat can see removable storage but not write there yet

The review must say `visible but not granted`, not `pick a folder and hope`.

### Receipt inbox is forced by platform

The flow must say `platform-fixed receipt inbox` and clearly separate that from ordinary subject binds.

### Recovery promises differ by storage class

If archive/history or restore support is weaker on removable storage, the product must surface that **before** the bind, not during restore.

### Existing-folder-only target

If the platform cannot create a new target on the selected storage class, the chooser must visibly switch from `create` semantics to `choose existing target` semantics.

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current official Resilio docs still leave too much meaning about landing roots, removable-storage grants, fixed inboxes, and degraded recovery promises scattered across Simple Mode, QR-intake instructions, SD-card troubleshooting, and archive caveats.
AnonSync should instead keep one acceptance contract where seat capability, storage consent, and degraded promises are visible together.
