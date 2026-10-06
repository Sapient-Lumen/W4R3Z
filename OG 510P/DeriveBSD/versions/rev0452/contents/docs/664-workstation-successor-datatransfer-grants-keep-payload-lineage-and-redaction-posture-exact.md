# Workstation successor data-transfer grants keep payload lineage and redaction posture exact

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` already made reviewed retry / re-offer continuity explicit through `renewal_posture` plus `supersedes_grant_digest`. `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md` then narrowed that path further: successor continuity is only for the same actor pair and the same-or-narrower typed offer envelope.

One more quiet drift remained inside that narrowed lane:
**a successor retry could still keep the same app pair and MIME/byte envelope while silently changing which payload lineage or redaction posture is crossing.**

This doc makes the next narrow cut:
**if `renewal_posture = supersedes-prior-grant`, successor continuity also requires exact `offer.content_source` and exact `offer.redaction_profile_digest` presence/value parity with the predecessor. Add/drop/swap of either field is fresh-grant required. `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md` then makes the next cut inside this narrowed lane explicit too: successor continuity also preserves payload digest, so semantic-equivalence rebinding is fresh-grant required rather than same-story folklore.**

See also:
- ADR: `adrs/ADR-0254-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- successor-scope boundary: `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- OCR text egress: `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.grant.retry.json`
- exact-payload boundary: `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`

## Why this needs a hard decision

Without this cut, successor continuity still leaves room for hidden authority drift:

- a trusted UI could say “allow again” while the underlying payload lineage changes,
- a broker could silently drop or replace `content_source` provenance on the successor,
- or a retry could swap redaction posture while staying inside the same MIME/byte envelope.

That would make “same reviewed transfer story” depend on broker memory and UI wording instead of the successor grant artifact itself.

## Accepted baseline

For the ordinary workstation lane:

- successor continuity still requires `successor_scope_posture = same-actor-pair-and-no-wider-offer`
- successor continuity must also keep payload lineage and redaction posture exact
- compared with the predecessor named by `supersedes_grant_digest`:
  - if `offer.content_source` is present, the successor must carry the exact same object
  - if `offer.content_source` is absent, the successor must also leave it absent
  - if `offer.redaction_profile_digest` is present, the successor must carry the exact same digest
  - if `offer.redaction_profile_digest` is absent, the successor must also leave it absent
- add/drop/swap of either field is **fresh-grant required** even if actor pair, direction, MIME, and byte bounds remain otherwise successor-shaped
- fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature)

This keeps “same story, try again” distinct from “different payload lineage or redaction posture, review it again.”

## What this buys

### 1) Successor continuity now means the same payload story too

The successor lane no longer means only “same apps and no wider envelope.” It also means the same payload lineage and the same redaction posture.

### 2) OCR/searchable follow-ons stay portable and auditable

The archive already lets clipboard egress preserve `content_source` provenance for OCR/searchable inspection output. This decision keeps that provenance from silently changing or disappearing on successor retry.

### 3) Detached support/export stays queryable without broker folklore

A support bundle can now answer why a later grant still counted as a continuation: it kept the same predecessor link, same actor pair, no-wider offer, and the same payload-lineage/redaction posture.

## What is explicitly not baseline

The ordinary workstation lane does **not** treat these as valid successor-shaped renewals:

- adding `offer.content_source` when the predecessor lacked it
- dropping `offer.content_source` that the predecessor had
- swapping to a different `offer.content_source`
- adding, dropping, or swapping `offer.redaction_profile_digest`
- treating trusted-UI retry wording as a substitute for a fresh wider/different reviewed grant

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/examples/ui.datatransfer.grant.retry.json`

Last updated: 2026-03-22r395
