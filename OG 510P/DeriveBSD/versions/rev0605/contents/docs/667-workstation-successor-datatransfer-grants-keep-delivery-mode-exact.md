# Workstation successor data-transfer grants keep delivery mode exact

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` already made reviewed retry / re-offer continuity explicit through `renewal_posture` plus `supersedes_grant_digest`. `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md` then narrowed that path to the same actor pair and same-or-narrower offer envelope. `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md` narrowed it again so payload lineage and redaction posture stay exact when present. `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md` then made the lane exact-payload-bound, and `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md` kept the foreground/interactivity posture exact too.

One more quiet widening seam still remained inside that already narrowed successor lane:
**a successor retry could still keep the same reviewed payload story while quietly changing `delivery_mode` from the ordinary one-shot lane to a multi-delivery exception lane.**

This doc makes the next narrow cut:
**if `renewal_posture = supersedes-prior-grant`, successor continuity must also keep `delivery_mode` exact. A successor grant reviewed as continuation of a `single-delivery` story must stay `single-delivery`; switching to or from `multi-delivery` is fresh-grant required.**

See also:
- ADR: `adrs/ADR-0257-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- predecessor-link boundary: `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- successor-scope boundary: `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- successor payload-lineage boundary: `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- successor exact-payload boundary: `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- successor foreground boundary: `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- successor rate-limit boundary: `docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md` (keeps `constraints.rate_limit` exact under successor continuity)
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- single-delivery baseline: `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.grant.retry.json`

## Why this needs a hard decision

Without this cut, successor continuity still leaves room for hidden replay-width drift:

- a trusted UI could say “allow again” while the later successor quietly becomes multi-delivery authority,
- a broker could preserve the same payload story while widening how many successful deliveries that authority permits,
- or support/export could have to guess whether the later retry was still the same reviewed one-shot act or a broader replay-capable grant disguised as continuity.

That would make “same reviewed transfer story” depend on broker-side convenience behavior instead of the portable successor grant artifact.

## Accepted baseline

For the ordinary workstation lane:

- successor continuity still requires `successor_scope_posture = same-actor-pair-and-no-wider-offer`
- successor continuity still keeps exact `offer.content_source`, exact `offer.redaction_profile_digest`, exact `offer.payload_digest`, exact `constraints.requires_foreground`, and exact actor-pair identity with the predecessor
- successor continuity must also keep `delivery_mode` exact
- compared with the predecessor named by `supersedes_grant_digest`:
  - if the predecessor carried `delivery_mode = single-delivery`, the successor must also carry `single-delivery`
  - if the predecessor carried `delivery_mode = multi-delivery`, the successor must also carry `multi-delivery`
  - any swap between those values is **fresh-grant required**
- fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature)

This keeps “same story, try again” distinct from “same bytes, but broader replay/reuse semantics, review it again.”

## What this buys

### 1) Successor continuity now means the same delivery semantics too

The successor lane no longer means only “same apps, same payload, same interactivity posture.” It also means the same one-shot vs multi-delivery contract that shaped the reviewed transfer act.

### 2) Single-delivery review no longer quietly inherits replay authority

`docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md` already fixed the ordinary lane as one-shot. This decision keeps successor continuity from becoming a loophole that silently widens one-shot review into a replay-capable lane.

### 3) Detached support/export stays queryable without broker folklore

A support bundle can now answer why a later grant still counted as a continuation: it kept the same predecessor link, same actor pair, no-wider offer, same lineage/redaction posture, same payload digest, same foreground posture, and the same `delivery_mode`.

## What is explicitly not baseline

The ordinary workstation lane does **not** treat these as valid successor-shaped renewals:

- switching `delivery_mode` from `single-delivery` to `multi-delivery`
- switching `delivery_mode` from `multi-delivery` to `single-delivery`
- treating broker retry policy, clipboard history, or lease reuse as a substitute for exact reviewed delivery semantics
- using “allow again” wording to widen how many deliveries the reviewed transfer authority permits

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- `spec/ui.datatransfer.grant.schema.json`

Last updated: 2026-03-22r398
