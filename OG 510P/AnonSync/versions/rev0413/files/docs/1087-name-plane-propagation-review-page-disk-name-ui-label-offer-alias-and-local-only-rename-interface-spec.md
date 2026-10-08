# Name-plane propagation review page: disk name, UI label, offer alias, and local-only rename

## Purpose

This page exists for the more common case where the name itself may be portable, but the human is still changing the wrong plane.
The review prevents accidental peer-visible rename when the intended change was only cosmetic, or accidental local-only rename when the intention was global.

## Core decision

Every name mutation must declare its plane explicitly.
The product should never force the operator to infer from context whether they changed:

- the local disk basename,
- the local presented title,
- the portable artifact label,
- the peer-visible alias,
- or the canonical portable name.

## Fixed page order

1. **Requested plane mutation**
2. **Observer / propagation map**
3. **Continuity and ambiguity warnings**
4. **Apply choices and receipt promise**

### 1) Requested plane mutation

Show a radio-group or segmented choice that names the selected plane in plain language:

- `Rename the folder on this device only`
- `Retitle it in the interface only`
- `Change the label used in exported offers`
- `Change the canonical name peers receive`
- `Keep names as they are; emit explanation only`

The operator must be able to answer: **which plane am I actually changing?**

### 2) Observer / propagation map

Show a matrix with rows for observer classes:

- current seat
- linked seats under same operator
- remote peers
- future exported offers
- logs / receipts

Each row shows `changes`, `unchanged`, or `recomputed later`.

The operator must be able to answer: **who will notice?**

### 3) Continuity and ambiguity warnings

Warn whenever:

- a local disk rename may be mistaken for a peer-visible rename
- a cosmetic title change leaves the disk path unchanged
- an offer label diverges from both disk and canonical name
- a local-only folder rename stays local by design
- a cross-root move is being confused with a rename

The operator must be able to answer: **what will stay different after apply?**

### 4) Apply choices and receipt promise

Only honest choices may appear:

- `Apply local-only rename`
- `Apply interface title change`
- `Apply offer-label change`
- `Open canonical propagation review`
- `Open cross-root rehome review`
- `Cancel and emit explanation`

Receipt must preserve:

- plane mutated
- audiences changed
- audiences unchanged
- blocked stronger sentence

## Public objects

### Name-plane propagation review

Fields:

- `name_plane_propagation_review_id`
- `subject_ref`
- `requested_plane`
- `current_values_by_plane`
- `observer_map`
- `continuity_warnings[]`
- `chosen_action` nullable
- `generated_at`

## Compact explanation strip

Example:

```text
This change renames the folder only on this device. Peers keep the current canonical name, and future offers keep their existing label unless changed separately.
```

## CLI implications

Minimum commands:

```text
anonsync names plane review --subject <subject> --plane <plane>
anonsync names plane apply <name_plane_propagation_review_id>
anonsync names plane receipt show <receipt_id>
```

