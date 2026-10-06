# Workstation successor data-transfer grants keep rate-limit posture exact

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` already made reviewed retry / re-offer continuity explicit through `renewal_posture` plus `supersedes_grant_digest`. `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md` then narrowed that path to the same actor pair and same-or-narrower offer envelope. `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md` narrowed it again so payload lineage and redaction posture stay exact when present. `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md` then made the lane exact-payload-bound, `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md` kept the foreground/interactivity posture exact, and `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md` kept replay width exact too. `docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md` then makes the next timing cut inside this already narrowed lane explicit too: successor continuity also preserves exact `constraints.expires_at`, so outer deadline posture drift is fresh-grant required rather than old-story folklore.

One more quiet execution-posture seam still remained inside that already narrowed successor lane:
**a successor retry could still keep the same reviewed payload story while quietly changing `constraints.rate_limit`, making the same reviewed transfer authority usable at a different tempo or throughput than the one originally reviewed.**

This doc makes the next narrow cut:
**if `renewal_posture = supersedes-prior-grant`, successor continuity must also keep `constraints.rate_limit` exact. A successor grant reviewed as continuation of a rate-limited transfer story must keep presence/value parity for `constraints.rate_limit`; add/drop/swap is fresh-grant required.**

See also:
- ADR: `adrs/ADR-0258-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md`
- predecessor-link boundary: `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- successor-scope boundary: `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- successor payload-lineage boundary: `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- successor exact-payload boundary: `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- successor foreground boundary: `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- successor delivery-mode boundary: `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- successor absolute-expiry boundary: `docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.grant.retry.json`

## Why this needs a hard decision

Without this cut, successor continuity still leaves room for hidden execution-tempo drift:

- a trusted UI could say “allow again” while the later successor quietly removes throttling or adopts a looser burst/throughput posture,
- a broker could preserve the same payload story while changing how fast the reviewed authority may be exercised,
- or support/export could have to guess whether the later retry was still the same reviewed act or a different execution-tempo grant disguised as continuity.

That would make “same reviewed transfer story” depend on broker-side throttling policy instead of the portable successor grant artifact.

## Accepted baseline

For the ordinary workstation lane:

- successor continuity still requires `successor_scope_posture = same-actor-pair-and-no-wider-offer`
- successor continuity still keeps exact `offer.content_source`, exact `offer.redaction_profile_digest`, exact `offer.payload_digest`, exact `constraints.requires_foreground`, and exact `delivery_mode`
- under `renewal_posture = supersedes-prior-grant`, `constraints.rate_limit` must also keep **presence/value parity** with the predecessor named by `supersedes_grant_digest`
- if the predecessor carried `constraints.rate_limit`, the successor must also carry it
- if the predecessor omitted `constraints.rate_limit`, the successor must also omit it
- if both carry `constraints.rate_limit`, the string value must match exactly
- fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature)
- add/drop/swap of `constraints.rate_limit` is **fresh-grant required** even if every other successor continuity field still matches

This keeps “same story, try again” distinct from “same payload, different execution tempo, review it again.”

## What this buys

### 1) Successor continuity stops being a stealth throughput-escalation lane

A reviewed retry can stay ergonomic without becoming a way to loosen throttling or burst posture under familiar wording. The successor path stays for renewing the same crossing, not for quietly changing how fast that authority may be exercised.

### 2) Trusted UI and broker behavior get a boring implementation target

Trusted UI can keep “allow again” language, but the implementation target is now clearer:
**either mint a same-story successor grant with the same `constraints.rate_limit`, or mint a fresh grant because the tempo/throughput contract really changed.**

### 3) Detached support/export can explain why a later grant counted as a continuation

`docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md` already lets receipts point back to the exact consumed grant. `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` already lets grants point back to the exact predecessor they superseded. This doc fixes the next query too:
**why did that successor count as a continuation? because it kept the same execution-tempo posture instead of changing `constraints.rate_limit` under the old story.**

## What is explicitly not baseline

The ordinary workstation lane does **not** treat these as valid successor-shaped renewals:

- adding `constraints.rate_limit` when the predecessor omitted it
- removing `constraints.rate_limit` when the predecessor carried it
- swapping to a different `constraints.rate_limit` string under successor continuity
- using “allow again” wording to widen or tighten throttling semantics without a fresh reviewed grant

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- `spec/ui.datatransfer.grant.schema.json`

Last updated: 2026-03-22r399
