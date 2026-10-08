# File-send ledger, expiry, retention, and byte-truth interface spec

## Purpose

The archive already had snapshot-send lineage and staged-transfer visibility language.
What it still lacked was one explicit contract for a smaller but very common seam:

> the difference between a transfer record, a still-redeemable offer, and local bytes that happen to remain on disk.

Current official Resilio docs make this seam sharper than a generic `shared links history` feature.
They still say mobile `Shared links` lists both uploaded and downloaded transfers, that received files also appear in a `Downloads` folder, that file-send links are valid for three days and currently cannot be changed, that iOS can remove a downloaded file from the device while its transfer history still remains visible, and that removing an item from `Shared links` can remove it only from Sync UI while the file remains on the system.
Current power-user preferences also still define how many expired transfers or how many days of expired transfers remain in the UI.

That is all useful.
It is still not a good object model.
A visible row in history is not the same thing as a redeemable offer, and neither is the same thing as bytes still resident on the seat.

## Core decision

AnonSync should split one-time handoff state into three explicit objects:

- **offer window** — can anyone still redeem this handoff?
- **ledger row** — what historical record remains visible?
- **byte residency** — do local payload bytes still exist on this seat?

Any action that changes one of those must say whether the other two change too.

## Why this matters

Current Resilio docs still reveal four interface mistakes AnonSync should not clone:

- expiry and retention can be different but are easy to read as the same thing
- a row can remain visible after bytes are gone
- bytes can remain after the row is hidden from one surface
- fixed mobile inboxes make it even easier to confuse `download history`, `downloaded bytes`, and `share offer`

AnonSync should therefore keep one stronger rule:

> a transfer list row is never the canonical truth about where the bytes are or whether the handoff is still live.

## Fixed review order

Every one-time handoff surface should render the same sections in the same order:

1. **Offer window**
2. **Ledger retention**
3. **Local byte presence**
4. **Removal consequence**

### 1) Offer window

This section should show:

- whether the handoff is still redeemable
- expiry time
- whether expiry is fixed or operator-chosen
- whether reissue creates a new offer or extends the same one

The operator must be able to answer: **can anyone still use this handoff?**

### 2) Ledger retention

This section should show:

- whether the row is active, expired, hidden, or archived from view
- how long expired rows remain visible
- what evidence the row preserves after expiry
- whether hiding the row is cosmetic or destructive

The operator must be able to answer: **what historical proof remains even if the transfer is over?**

### 3) Local byte presence

This section should show:

- whether bytes still exist locally
- where they live
- whether they are ordinary subject bytes, receipt-inbox bytes, or temporary transfer bytes
- whether deleting them changes the ledger or the offer window

The operator must be able to answer: **do the bytes still exist here, and what kind of local copy are they?**

### 4) Removal consequence

This section should show distinct actions such as:

- `hide row only`
- `delete local payload only`
- `revoke live offer`
- `purge row and local payload`

Each must declare which of the three objects changes.

The operator must be able to answer: **what exactly disappears if I press this?**

## Main surface

AnonSync should show one compact state stack for each handoff:

- `offer expired`
- `ledger retained 30d`
- `local payload still present`

or:

- `offer revoked`
- `ledger hidden from Home`
- `payload removed from this seat`

The product must never make the operator infer byte truth from a lingering history row.

## Object model implications

AnonSync should add or strengthen these objects:

- `snapshot_offer_window`
- `transfer_ledger_entry`
- `transfer_payload_presence`
- `transfer_removal_review`
- `transfer_retention_receipt`

Suggested fields for `transfer_ledger_entry`:

- `transfer_id`
- `subject_kind`
- `offer_state`
- `expiry_at`
- `ledger_visibility`
- `retention_until`
- `local_payload_presence`
- `payload_path`

## Event language

Use explicit phrases such as:

- `offer expired; ledger retained`
- `payload removed from receipt inbox; ledger preserved`
- `row hidden from UI only; local payload unchanged`
- `live offer revoked; bytes on this seat unchanged`

Avoid vague lines such as:

- `removed`
- `cleared`
- `expired item deleted`

## CLI shape

Example commands:

```text
anonsync transfer show <id>
anonsync transfer retention review <id>
anonsync transfer remove <id> --row-only
anonsync transfer remove <id> --payload-only
anonsync transfer receipt <id>
```

The CLI must expose the same split between offer, ledger, and bytes as the local web UI.

## Failure and edge cases

### Expired offer but bytes still local

The product should say exactly that.
No resurrection or cleanup action should pretend the payload vanished merely because redemption ended.

### Row hidden but bytes remain on disk

This must be classified as visibility change, not deletion.

### Bytes deleted but ledger retained for audit

That is allowed and often useful.
The row must clearly say that the payload is gone.

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current official Resilio docs still let expiry, history retention, UI removal, and on-disk bytes drift apart across several surfaces.
AnonSync should instead expose one transfer ledger where offer truth, row truth, and byte truth are visibly separate.
