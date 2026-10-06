# Workstation successor data-transfer grants stay exact-payload-bound and no semantic-equivalence rebinding

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` already made reviewed retry / re-offer continuity explicit through `renewal_posture` plus `supersedes_grant_digest`. `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md` then narrowed that path to the same actor pair and same-or-narrower offer envelope. `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md` narrowed it again so payload lineage and redaction posture stay exact when present.

One more quiet drift still remained inside that already narrowed lane:
**a successor retry could still keep the same actor pair, envelope, payload lineage, and redaction posture while silently rebinding to newly rendered or semantically equivalent payload bytes.**

This doc makes the next narrow cut:
**if `renewal_posture = supersedes-prior-grant`, successor continuity is exact-payload-bound. Successor grants must carry exact payload digest (`offer.payload_digest`) parity with the predecessor, and semantic-equivalence/substitution is fresh-grant required.**

See also:
- ADR: `adrs/ADR-0255-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- predecessor-link boundary: `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- successor-scope boundary: `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- successor payload-lineage boundary: `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- OCR text egress: `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/ui.datatransfer.receipt.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.grant.retry.json`, `spec/examples/ui.datatransfer.receipt.json`

## Why this needs a hard decision

Without this cut, successor continuity still leaves room for hidden substitution drift:

- a trusted UI could say “allow again” while the source app re-renders different bytes,
- a broker could quietly normalize or re-serialize a payload and call it “the same transfer,”
- or a retry could substitute semantically equivalent content while keeping the same actor pair, MIME set, lineage hints, and redaction posture.

That would make “same reviewed transfer story” depend on local broker ideas about equivalence instead of a portable artifact boundary.

## Accepted baseline

For the ordinary workstation lane:

- successor continuity still requires `successor_scope_posture = same-actor-pair-and-no-wider-offer`
- successor continuity still keeps exact `offer.content_source` and exact `offer.redaction_profile_digest` presence/value parity
- successor continuity must also be **exact-payload-bound**
- `ui.datatransfer.grant.offer.payload_digest` is the digest of the exact offered payload for that reviewed transfer story
- compared with the predecessor named by `supersedes_grant_digest`:
  - the successor must carry `offer.payload_digest`
  - the predecessor must also have carried `offer.payload_digest`
  - the successor value must be exactly equal to the predecessor value
- `ui.datatransfer.receipt.summary.payload_digest` should echo the exact transferred payload digest
- semantic-equivalence rebinding, re-rendering, re-serialization, add/drop of payload digest, or substitution under the old story is **fresh-grant required**
- fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature)

This keeps “same story, try again” distinct from “different bytes that look close enough, review it again.” `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md` then fixes the next execution-posture cut: even the same exact reviewed bytes must keep exact `constraints.requires_foreground`, so successor continuity does not quietly become background-capable.

## What this buys

### 1) Successor continuity now means the same reviewed bytes too

The successor lane no longer means only “same apps, same envelope, same lineage hints.” It also means the same reviewed payload binding.

### 2) OCR/searchable follow-ons stay exportable without semantic-folklore joins

OCR-derived text can already preserve `content_source`. This decision keeps later successor retry from treating “same extracted phrase, but regenerated now” as the same reviewed payload without saying so explicitly on a fresh grant.

### 3) Detached support/export stays queryable without broker notes

A support bundle can now answer why a later grant still counted as a continuation: it kept the same predecessor link, same actor pair, no-wider offer, same payload lineage/redaction posture, and the same payload digest (`offer.payload_digest`).

## What is explicitly not baseline

The ordinary workstation lane does **not** treat these as valid successor-shaped renewals:

- adding `offer.payload_digest` when the predecessor lacked it
- dropping `offer.payload_digest` that the predecessor had
- swapping to a different `offer.payload_digest`
- re-rendering, re-serializing, or substituting semantically equivalent payload bytes under the old reviewed transfer story
- treating `offer.id`, trusted-UI wording, or broker history as a substitute for exact payload binding

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`
- `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`

Last updated: 2026-03-22r396
