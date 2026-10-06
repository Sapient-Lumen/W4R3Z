# Workstation data-transfer constraints stay closed-world and no hidden successor posture

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` already made reviewed retry / re-offer continuity explicit through `renewal_posture` plus `supersedes_grant_digest`. `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md` narrowed that path to the same actor pair and same-or-narrower offer envelope. `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`, `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`, `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`, `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`, `docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md`, and `docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md` then made the currently typed successor posture exact.

One more quiet seam still remained:
**`ui.datatransfer.grant.constraints` was still an open-world object, so an implementation could keep every currently named successor-parity field exact while quietly adding some extra `constraints.*` key that changed how authority was exercised.**

This doc makes the next narrow cut:
**ordinary workstation `ui.datatransfer.grant.constraints` is now a closed-world typed vocabulary. There is no hidden successor execution posture beyond the already accepted typed keys; future extra posture needs an ADR/spec change or a distinct richer transfer lane.**

See also:
- ADR: `adrs/ADR-0260-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- successor-lineage boundary: `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- successor-scope boundary: `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- successor payload-lineage boundary: `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- successor exact-payload boundary: `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- successor foreground boundary: `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- successor delivery-mode boundary: `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- successor rate-limit boundary: `docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md`
- successor absolute-expiry boundary: `docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md`
- schema/example: `spec/ui.datatransfer.grant.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.grant.retry.json`

## Why this needs a hard decision

Without this cut, the archive still leaves one open-ended place for hidden authority drift:

- a broker can preserve every currently reviewed successor field while adding some extra product-local `constraints.*` key,
- a trusted UI can keep familiar retry wording while the real exercise posture quietly changes in implementation-private vocabulary,
- or detached support/export has no stable way to tell whether “same reviewed transfer story” exhausted the execution posture the archive actually meant to review.

That would keep the real contract in private broker vocabulary instead of the portable artifact.

## Accepted baseline

For the ordinary workstation lane:

- `ui.datatransfer.grant.constraints` is a **closed-world typed object**
- the baseline typed keys are exactly `requires_foreground`, `rate_limit`, and `expires_at`
- unknown extra `constraints.*` keys are **not baseline** for ordinary workstation transfer
- successor continuity still keeps exact `offer.content_source`, exact `offer.redaction_profile_digest`, exact `offer.payload_digest`, exact `constraints.requires_foreground`, exact `delivery_mode`, exact `constraints.rate_limit`, and exact `constraints.expires_at`
- because the vocabulary is now closed-world, there is no hidden successor execution posture beyond those already accepted typed keys
- if future transfer posture is worth standardizing, it should come back through an ADR/spec update or a distinct richer lane, not through arbitrary per-implementation `constraints.*`
- fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature)

This keeps “same reviewed transfer story” finite, typed, and portable.

## What this buys

### 1) Successor continuity stops one layer earlier

The archive no longer has to keep asking whether some unnamed `constraints.*` field should also be frozen under successor continuity, because the ordinary lane no longer admits hidden extra constraint vocabulary in the first place.

### 2) Trusted UI and support/export get one shared review surface

A trusted UI can render one finite set of reviewed execution-posture fields, and detached tooling can explain the same finite set later. That is better than letting each implementation invent one more quiet `constraints.*` knob and then teaching support to reverse-engineer it.

### 3) Future richer posture is still possible, but explicit

This does **not** say no future multi-delivery or richer authority lane can ever exist. It says the ordinary workstation lane must not sneak future richness in through an open-ended `constraints` bag. If another posture is worth implementing, it should be named, justified, and wired through the archive on purpose.

## What is explicitly not baseline

The ordinary workstation lane does **not** treat these as baseline:

- product-local hidden `constraints.*` keys on `ui.datatransfer.grant`
- successor continuity that depends on implementation-private constraint names
- profile-specific private extensions to the ordinary portable grant artifact
- leaving the archive open-ended on “one more hidden posture field” after the already accepted successor boundary cuts

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
- `docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md`
- `docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md`
- `spec/ui.datatransfer.grant.schema.json`

Last updated: 2026-03-22r400
