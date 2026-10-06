# Workstation successor data-transfer grants keep foreground requirement exact

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` already made reviewed retry / re-offer continuity explicit through `renewal_posture` plus `supersedes_grant_digest`. `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md` then narrowed that path to the same actor pair and same-or-narrower offer envelope. `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md` narrowed it again so payload lineage and redaction posture stay exact when present. `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md` then made that lane exact-payload-bound.

One more quiet drift still remained inside that already narrowed lane:
**a successor retry could still keep the same actor pair, envelope, lineage, redaction posture, and exact payload bytes while quietly changing the foreground/interactivity posture of the transfer.**

This doc makes the next narrow cut:
**if `renewal_posture = supersedes-prior-grant`, successor continuity must also keep `constraints.requires_foreground` exact when present. Add/drop/swap of the foreground requirement is fresh-grant required. `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md` then fixes the next replay-width cut: successor continuity must also keep `delivery_mode` exact, so reviewed one-shot authority cannot quietly become multi-delivery retry authority.**

See also:
- ADR: `adrs/ADR-0256-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- predecessor-link boundary: `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- successor-scope boundary: `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- successor payload-lineage boundary: `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- successor exact-payload boundary: `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- host/app boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.grant.retry.json`
- successor delivery-mode boundary: `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`

## Why this needs a hard decision

Without this cut, successor continuity still leaves room for hidden interactivity drift:

- a trusted UI could say “allow again” while the later successor silently becomes background-capable,
- a broker could preserve the same payload story while dropping the foreground visibility requirement that shaped the earlier review,
- or support/export could have to guess whether the later retry was still the same reviewed foreground-gated act or a different background-capable authority grant disguised as continuity.

That would make “same reviewed transfer story” depend on current broker behavior and UI expectation instead of the portable successor grant artifact.

## Accepted baseline

For the ordinary workstation lane:

- successor continuity still requires `successor_scope_posture = same-actor-pair-and-no-wider-offer`
- successor continuity still keeps exact `offer.content_source`, exact `offer.redaction_profile_digest`, and exact `offer.payload_digest` parity with the predecessor
- successor continuity must also keep foreground/interactivity posture exact through `constraints.requires_foreground`
- compared with the predecessor named by `supersedes_grant_digest`:
  - if `constraints.requires_foreground` is present, the successor must also carry it
  - if `constraints.requires_foreground` is absent, the successor must also leave it absent
  - when present, the successor value must be exactly equal to the predecessor value
- add/drop/swap of `constraints.requires_foreground` is **fresh-grant required** even if actor pair, offer scope, lineage, redaction posture, and payload digest remain otherwise successor-shaped
- fresh issuance details may still change (`lease_id`, `offer.id`, `issued_at`, `effective_until`, signature)

This keeps “same story, try again” distinct from “same bytes, but different backgroundability/interactivity contract, review it again.” The next accepted cut also keeps the same reviewed delivery semantics exact, so a one-shot reviewed transfer does not quietly become a replay-capable successor.

## What this buys

### 1) Successor continuity now means the same reviewed visibility posture too

The successor lane no longer means only “same apps, same envelope, same payload.” It also means the same foreground/interactivity requirement that shaped the reviewed transfer act.

### 2) Trusted UI gets a boring target for retry affordances

Trusted UI can keep ergonomic retry wording, but the implementation target is clearer:
**either mint a same-story successor grant with the same foreground requirement, or mint a fresh grant because the authority is becoming background-capable or otherwise changing interactivity posture.**

### 3) Detached support/export stays queryable without focus-state folklore

A support bundle can now answer why a later grant still counted as a continuation: it kept the same predecessor link, same actor pair, no-wider offer, same lineage/redaction posture, same payload digest, and the same `requires_foreground` posture.

## What is explicitly not baseline

The ordinary workstation lane does **not** treat these as valid successor-shaped renewals:

- adding `constraints.requires_foreground` when the predecessor lacked it
- dropping `constraints.requires_foreground` that the predecessor had
- switching `constraints.requires_foreground` from `true` to `false` or from `false` to `true`
- treating current window focus, broker policy, or trusted-UI wording as a substitute for exact reviewed interactivity posture

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
- `spec/ui.datatransfer.grant.schema.json`

Last updated: 2026-03-22r397
