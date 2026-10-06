# Workstation data-transfer renewals stay successor grants and predecessor-digest linked

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md` already fixed what happens after a successful ordinary transfer: the grant is spent and later recovery is a fresh explicit grant / re-offer required. `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md` then fixed the other terminal edge too: unused ordinary authority ends at exact `effective_until`, and late delivery fails closed.

One smaller but still expensive contract gap remained:
**when the human or policy really does say “allow again”, “copy again”, or “retry with a new review”, what keeps that act from becoming an in-place broker mutation instead of a new reviewed grant artifact?**

This doc makes the next narrow cut:
**reviewed workstation transfer renewal/re-offer must mint a fresh `ui.datatransfer.grant`, and if it continues an earlier transfer story it must say so explicitly with `renewal_posture = supersedes-prior-grant` plus exact `supersedes_grant_digest` rather than relying on `offer.id`, `lease_id`, recency, or broker-memory folklore.**

See also:
- ADR: `adrs/ADR-0252-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- data-transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- one-shot boundary: `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- exact lifetime boundary: `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- exact grant-join boundary: `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- OCR text-egress boundary: `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.grant.ocr-inspection-text.json`, `spec/examples/ui.datatransfer.grant.retry.json`

## Why this needs a hard decision

Without a tighter rule, “fresh grant / re-offer required” still leaves too much room for convenience drift:

- a broker may quietly extend the original grant in place after a timeout,
- a trusted UI may present “allow again” while reusing the old artifact identity under the hood,
- or support/export tooling may have to infer continuity from `offer.id`, `lease_id`, or “same app pair” folklore.

That would put the real retry/renewal contract back into control-plane state instead of the signed reviewed artifact, which is exactly the kind of drift the archive has been squeezing out elsewhere.

## Accepted baseline

For the ordinary workstation lane:

- `ui.datatransfer.grant` must carry `renewal_posture`
- `renewal_posture = fresh-grant` means this grant starts a new reviewed transfer story
- `renewal_posture = supersedes-prior-grant` means this grant is the reviewed successor of an earlier transfer grant
- successor grants must carry exact `supersedes_grant_digest`
- reviewed renewal/re-offer stays **new artifact plus predecessor digest**, not in-place extension of the earlier grant
- `offer.id`, `lease_id`, or repeated source/destination identities may remain useful correlates, but they are not the portable continuity answer
- if a reviewed successor really continues the same transfer story, the next boundary is scope: `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md` keeps successor continuity carrying `successor_scope_posture`, same-actor-pair, and no-wider-offer instead of letting retry wording hide a wider grant

This gives support/export one boring question to answer when transfer authority appears to continue:
**did a fresh grant start a new story, or did a reviewed successor grant explicitly supersede an earlier grant digest?**

## What this buys

### 1) “Allow again” stops being backend folklore

A human-visible retry can stay ergonomic without making the real policy live in broker rows.
The UI may still say “allow again,” but the durable answer is now a fresh reviewed artifact, optionally linked to the prior one by digest.

### 2) The one-shot and exact-deadline cuts stay honest

`docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md` already said successful ordinary transfer spends the grant.
`docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md` already said unused ordinary authority ends exactly.
This doc fixes the follow-on continuity rule:
**recovery or renewed approval stays successor-shaped instead of mutating the old grant story in place.**

### 3) Detached support/export can follow the whole transfer chain

`docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md` already lets receipts point back to the exact consumed grant.
Now the grant itself can also explain whether it began a new story or explicitly superseded a prior grant, so detached tooling can follow renewal lineage without opening broker databases.

## What is explicitly not baseline

The ordinary workstation lane does **not** treat these as equivalent to a reviewed successor grant:

- extending the deadline or state of an older grant in place
- inferring continuity from `offer.id` reuse alone
- inferring continuity from `lease_id` reuse alone
- assuming the newest grant for the same source/destination pair automatically replaces the earlier one

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/examples/ui.datatransfer.grant.retry.json`

Last updated: 2026-03-22r393
