# Workstation successor data-transfer grants stay same-actor-pair and no-wider-offer

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md` already fixed what happens after a successful ordinary transfer: the grant is spent and later recovery is a fresh explicit grant / re-offer required. `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md` then made unused authority end at exact `effective_until`, and `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` made reviewed retry/re-offer successor-shaped through `renewal_posture` plus `supersedes_grant_digest`.

One smaller but still expensive contract gap remained:
**once a reviewed retry can be a successor grant, what keeps that successor-shaped path from quietly widening the transfer instead of simply renewing the same reviewed transfer story?**

This doc makes the next narrow cut:
**if `renewal_posture = supersedes-prior-grant`, the successor grant must stay the same actor pair and same-or-narrower typed offer scope; broader source/destination or broader offer changes are fresh-grant required. `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md` makes the next cut inside that narrowed lane: payload lineage and redaction posture must stay exact too.**

See also:
- ADR: `adrs/ADR-0253-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- data-transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- one-shot boundary: `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- exact lifetime boundary: `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- successor-lineage boundary: `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- exact grant-join boundary: `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.grant.retry.json`

## Why this needs a hard decision

Without a tighter rule, "successor grant" still leaves too much room for convenience drift:

- a trusted UI may say “allow again” while quietly switching the destination app,
- a broker may reuse successor continuity while broadening MIME or byte limits,
- or support/export tooling may have to guess whether the later artifact was really the same transfer story or a new wider authority grant disguised as a retry.

That would turn reviewed continuity into a stealth widening lane, which is exactly the kind of ambient expansion the workstation archive has been trimming away.

## Accepted baseline

For the ordinary workstation lane:

- successor grants must carry `successor_scope_posture` = `same-actor-pair-and-no-wider-offer`
- `renewal_posture = supersedes-prior-grant` is only valid for the **same reviewed transfer story**
- compared with the predecessor named by `supersedes_grant_digest`, the successor must keep the same `subject`, `offer_source_subject`, `direction`, and `delivery_mode`
- compared with that predecessor, the successor offer may stay the same or become narrower on the currently typed offer envelope:
  - `offer.mime_types` stays equal or becomes a subset
  - `offer.max_bytes` stays equal or smaller
  - `offer.redaction_profile_digest` and `offer.content_source` do not silently switch to a different value under successor continuity when they are present
- newly minted artifact identity may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature)
- any actor-pair change or broader offer change is **fresh-grant required** even if humans think of the later act as a retry

This keeps “same story, try again” distinct from “new broader transfer, review it again.” The next accepted cut also keeps successor continuity from silently changing payload lineage or redaction posture.

## What this buys

### 1) Successor continuity stops being a stealth escalation lane

A reviewed retry can stay ergonomic without becoming a way to widen authority under familiar wording. The successor path stays for renewing the same crossing, not for quietly broadening it.

### 2) Trusted UI and broker behavior get a boring implementation target

Trusted UI can keep “allow again” language, but the implementation target is now clearer:
**either mint a same-story successor grant, or mint a fresh grant because scope really changed.**

### 3) Detached support/export can explain why a later grant counted as a continuation

`docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md` already lets receipts point back to the exact consumed grant. `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` already lets grants point back to the exact predecessor they superseded. This doc fixes the next query too:
**why did that successor count as a continuation? because it stayed the same actor pair and no-wider-offer, rather than widening scope under the old story.**

## What is explicitly not baseline

The ordinary workstation lane does **not** treat these as valid successor-shaped renewals:

- switching to a different source or destination compartment under the old transfer story
- broadening MIME types under successor continuity
- broadening `max_bytes` under successor continuity
- silently switching redaction/provenance posture under successor continuity
- quietly changing payload lineage or redaction posture while keeping the same actors and outer MIME/byte envelope
- using “allow again” wording as a substitute for a fresh wider reviewed grant

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `spec/ui.datatransfer.grant.schema.json`
- `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `spec/examples/ui.datatransfer.grant.retry.json`

Last updated: 2026-03-22r394
