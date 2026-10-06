# Workstation ordinary data-transfer baseline stays frozen and richer lanes are RFC-first

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` through `docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md` progressively narrowed the ordinary portable transfer lane until its successor continuity, payload identity, execution posture, timing posture, and constraints vocabulary are explicit and finite.

This doc makes the next higher-order cut explicit:
**the ordinary workstation `ui.datatransfer.grant` family is now the frozen portable baseline, complete enough to implement, and future richer transfer lanes are RFC-first rather than quiet growth of the same artifact family.**

See also:
- ADR: `adrs/ADR-0261-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- host/UI boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- anti-laundering boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- open questions / risk register: `docs/266-open-questions-and-risk-register.md`
- lessons index: `docs/110-juicy-os-lessons.md`
- schema/example: `spec/ui.datatransfer.grant.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.grant.retry.json`

## Why this needs a hard decision

Without a stopping rule, the archive keeps paying the same entropy cost twice:

- first by narrowing the ordinary reviewed-transfer lane,
- then by silently using that same lane as the place where richer transfer ideas sneak back in.

That makes the baseline artifact family unstable even when the archive already has a coherent enough ordinary answer.

## Accepted baseline

For ordinary workstation transfer:

- the current portable artifact family is the **frozen portable baseline**
- it is treated as **complete enough to implement**
- richer replay/batching, widened/substituting, directory-like, or otherwise broader transfer lanes are **RFC-first**
- those richer ideas are **not baseline** until accepted explicitly
- and any richer lane that is accepted later must mint a **distinct artifact family** instead of widening or variant-switching the ordinary `ui.datatransfer.grant` / `ui.datatransfer.receipt` family (`docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`)
- ordinary-lane follow-up work may still clarify wording, fix examples, tighten joins, or add anti-drift checks, but it must not quietly widen authority

## What this buys

### 1) A stable implementation target

The workstation story now has a transfer lane that can be implemented without waiting for every possible richer edge case to be designed up front.

### 2) A cleaner archive-management rule

The archive no longer has to pretend that every future transfer idea is just one more “small clarification” of the same baseline artifact family.

### 3) Better profile portability

A/B/C/D can share one boring ordinary reviewed-transfer floor while any future richer lane can justify itself explicitly by profile, tier, and operator need.

## What is explicitly not baseline

The ordinary portable baseline does **not** include:

- quiet widening of the same `ui.datatransfer.grant` shape
- replay/batching semantics added by documentation drift alone
- substitution/re-render authority added by successor wording drift alone
- collection-like or directory-like authority smuggled into the same ordinary artifact family
- product-local “just for this profile” richer transfer behavior without RFC/ADR acceptance

## Research note

This stop-point also matches a common systems pattern: keep the ordinary user-mediated transfer lane narrow and explicit, then add richer mediated lanes separately when needed. XDG desktop portals separate mediated desktop capability acquisition behind explicit portal interfaces rather than one ambient file/clipboard capability surface. Android likewise distinguishes the Photo Picker’s narrow selected-media lane from the broader Storage Access Framework document-provider lane. See the portal/powerbox references collected in `docs/32-curated-references.md`.

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
- `docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md`
- `spec/ui.datatransfer.grant.schema.json`

Last updated: 2026-03-22r402
