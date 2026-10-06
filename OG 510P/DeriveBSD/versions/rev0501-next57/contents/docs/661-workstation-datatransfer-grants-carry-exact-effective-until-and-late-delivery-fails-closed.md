# Workstation data-transfer grants carry exact effective-until and late delivery fails closed

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/538-workstation-cross-domain-datatransfer-floor.md` already fixed the ordinary workstation data-transfer posture: cross-domain clipboard/file movement is explicit, directional, and single-delivery by default instead of an ambient shared clipboard. `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md` then made the consumed grant artifact exact, and `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md` made the ordinary lane one-shot after the first successful read-side transfer.

One small but still expensive contract gap remained:
**the archive still made readers reconstruct grant lifetime from `issued_at`, `offer.ttl_seconds`, and maybe `constraints.expires_at` instead of carrying one exact answer on the grant artifact itself.**

This doc makes the next narrow cut:
**ordinary workstation `ui.datatransfer.grant` artifacts must carry exact `effective_until`, and successful ordinary transfer after that point fails closed instead of relying on late-delivery grace periods, stale-offer reuse, or broker-memory folklore.**

See also:
- ADR: `adrs/ADR-0251-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- data-transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- one-shot boundary: `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- OCR text-egress boundary: `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- exact actor and grant joins: `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`, `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/ui.datatransfer.receipt.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.receipt.json`, `spec/examples/ui.datatransfer.grant.ocr-inspection-text.json`, `spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json`

## Why this needs a hard decision

Without a tighter rule, grant lifetime still leaves too much room for convenience drift:

- one implementation may treat `ttl_seconds` as advisory while another enforces `constraints.expires_at`,
- a broker may accept a transfer slightly after timeout because the offer was already open,
- or support/export tooling may have to guess whether a late receipt still counted as ordinary policy.

That is out of character for the rest of the archive, which has been slowly moving toward exact joins instead of reconstructing operational meaning from multiple soft hints.

## Accepted baseline

For the ordinary workstation lane:

- `ui.datatransfer.grant` must carry exact `effective_until`
- `effective_until` is the **exact end of ordinary transfer authority** for that grant artifact
- if `offer.ttl_seconds` and/or `constraints.expires_at` are also present, `effective_until` must be **no later than** those bounds
- successful ordinary transfer must not occur later than the joined grant `effective_until`
- late delivery after `effective_until` fails closed
- ordinary retry/recovery after expiry is **fresh explicit grant / re-offer required**, not stale offer reuse or broker grace-period folklore

This gives support/export one boring question to answer: **what was the exact transfer deadline on the reviewed grant artifact?**

## What this buys

### 1) Lifetime becomes exact evidence instead of folklore

Readers no longer have to reconstruct effective authority from several optional timing fields.
The grant itself now publishes the exact end of ordinary authority.

### 2) The one-shot rule gets a real terminal boundary

`docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md` already made successful delivery terminal.
This doc fixes the other half: **late unused authority also ends exactly**.

### 3) OCR/text egress stays bounded all the way through

The OCR text-egress lane was already explicit, plain-text, and single-delivery by default.
Now copied OCR-derived text also keeps an exact time boundary instead of inheriting broker-specific timeout folklore.

## What is explicitly not baseline

The ordinary workstation lane does **not** treat these as equivalent to valid ordinary transfer:

- accepting a successful read-side transfer after `effective_until`
- inferring lifetime only from `ttl_seconds` while ignoring the explicit grant deadline
- treating broker-local grace periods as ordinary policy
- replaying or reusing a stale offer after expiry instead of minting a fresh grant

The next continuity cut now stays explicit too: `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` requires any reviewed retry/re-offer to mint a fresh successor-shaped grant with `renewal_posture` plus `supersedes_grant_digest` instead of extending the earlier grant in place.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`

Last updated: 2026-03-22r392
