# Workstation successor data-transfer grants keep absolute expiry posture exact

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` already made reviewed retry / re-offer continuity explicit through `renewal_posture` plus `supersedes_grant_digest`. `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md` then narrowed that path to the same actor pair and same-or-narrower offer envelope. `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md` narrowed it again so payload lineage and redaction posture stay exact when present. `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md` then made the lane exact-payload-bound, `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md` kept the foreground/interactivity posture exact, `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md` kept replay width exact, and `docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md` kept throttling posture exact too.

One more quiet timing-posture seam still remained inside that already narrowed successor lane:
**a successor retry could still keep the same reviewed payload story while quietly changing `constraints.expires_at`, which would replace the outer absolute-expiry explanation for the grant even if the current `effective_until` still looked acceptable.**

This doc makes the next narrow cut:
**if `renewal_posture = supersedes-prior-grant`, successor continuity must also keep `constraints.expires_at` exact. A successor grant reviewed as continuation of the same transfer story must keep presence/value parity for `constraints.expires_at`; add/drop/swap is fresh-grant required.**

See also:
- ADR: `adrs/ADR-0259-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md`
- exact lifetime boundary: `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- predecessor-link boundary: `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- successor-scope boundary: `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- successor payload-lineage boundary: `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- successor exact-payload boundary: `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- successor foreground boundary: `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- successor delivery-mode boundary: `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- successor rate-limit boundary: `docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.grant.retry.json`

## Why this needs a hard decision

Without this cut, successor continuity still leaves room for hidden absolute-expiry drift:

- a trusted UI could say “allow again” while the later successor quietly removes the outer absolute-expiry ceiling,
- a broker could preserve the same payload story while swapping to a different `constraints.expires_at` than the one originally reviewed,
- or support/export could have to guess whether the later retry was still the same reviewed act or a differently time-bounded grant disguised as continuity.

That would make “same reviewed transfer story” depend on hidden policy interpretation instead of the portable successor grant artifact.

## Accepted baseline

For the ordinary workstation lane:

- successor continuity still requires `successor_scope_posture = same-actor-pair-and-no-wider-offer`
- successor continuity still keeps exact `offer.content_source`, exact `offer.redaction_profile_digest`, exact `offer.payload_digest`, exact `constraints.requires_foreground`, exact `delivery_mode`, and exact `constraints.rate_limit`
- under `renewal_posture = supersedes-prior-grant`, `constraints.expires_at` must also keep **presence/value parity** with the predecessor named by `supersedes_grant_digest`
- if the predecessor carried `constraints.expires_at`, the successor must also carry it
- if the predecessor omitted `constraints.expires_at`, the successor must also omit it
- if both carry `constraints.expires_at`, the timestamp must match exactly
- `effective_until` still stays the exact current grant deadline and must be no later than `constraints.expires_at` when present
- fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature)
- add/drop/swap of `constraints.expires_at` is **fresh-grant required** even if every other successor continuity field still matches

This keeps “same story, try again” distinct from “same payload, different outer deadline semantics, review it again.”

## What this buys

### 1) Successor continuity stops being a stealth expiry-ceiling rewrite

A reviewed retry can stay ergonomic without becoming a way to remove or replace the absolute outer deadline under familiar wording.
The later grant may still choose a new `effective_until` inside the same ceiling, but it does not get to pretend the ceiling itself never changed.

### 2) `effective_until` keeps its role without swallowing all timing meaning

`docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md` already made `effective_until` the exact current grant deadline.
This doc keeps the optional outer ceiling meaningful too: if a transfer story was reviewed with `constraints.expires_at`, successor continuity preserves that same outer bound instead of quietly rewriting it. `docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md` then closes the next open-ended seam too by making `ui.datatransfer.grant.constraints` a closed-world typed vocabulary, so no hidden extra successor posture remains behind private `constraints.*` names.

### 3) Detached support/export can explain *why* the deadline stayed bounded

Portable evidence can now distinguish:
- a successor that stayed under the same absolute expiry posture, from
- a fresh reviewed grant that really changed or removed that posture.

That is more explainable than leaving later readers to infer deadline semantics from broker policy or UI wording.

## What is explicitly not baseline

The ordinary workstation lane does **not** treat these as valid successor-shaped renewals:

- adding `constraints.expires_at` when the predecessor omitted it
- removing `constraints.expires_at` when the predecessor carried it
- swapping to a different `constraints.expires_at` timestamp under successor continuity
- treating “same `effective_until` right now” as enough proof that the outer expiry posture stayed the same

The next timing cut, if there is one worth making, should be driven by a concrete richer time-bounded lane rather than by leaving ordinary successor continuity fuzzy.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- `docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md`
- `docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md`
- `spec/ui.datatransfer.grant.schema.json`

Last updated: 2026-03-22r400
