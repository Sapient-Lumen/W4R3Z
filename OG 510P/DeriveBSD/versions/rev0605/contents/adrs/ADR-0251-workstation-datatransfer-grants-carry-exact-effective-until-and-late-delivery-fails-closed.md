# ADR-0251: Workstation data-transfer grants carry exact effective-until and late delivery fails closed

## Status
Accepted

## Context

`adrs/ADR-0128-workstation-cross-domain-datatransfer-floor.md` already fixed the ordinary workstation data-transfer posture: explicit cross-domain transfer, no ambient shared clipboard, and single-delivery as the boring default. `ADR-0249` then made receipts joinable back to the exact reviewed grant artifact through `grant_digest`, and `ADR-0250` made the ordinary lane one-shot after the first successful read-side delivery.

One small but still practical ambiguity remained:
**what exact time boundary ends ordinary transfer authority for a reviewed grant artifact?**

If the archive leaves that fuzzy, implementations drift toward lifetime folklore:

- reconstructing authority from `issued_at` plus `offer.ttl_seconds`,
- sometimes preferring `constraints.expires_at`,
- or accepting slightly late deliveries because the broker still had local state.

## Decision

For the ordinary workstation lane:

1. `ui.datatransfer.grant` must carry exact `effective_until`.
2. `effective_until` is the exact end of ordinary transfer authority for that grant artifact.
3. If `offer.ttl_seconds` and/or `constraints.expires_at` are present, `effective_until` must be no later than those bounds.
4. Successful ordinary transfer must not occur later than the joined grant `effective_until`.
5. late delivery after `effective_until` fails closed.
6. Ordinary retry after expiry is a fresh explicit grant / re-offer, not stale-offer reuse or broker grace-period folklore.

## Consequences

### Positive
- Transfer lifetime becomes exact evidence instead of reconstruction.
- Detached support/export can answer the deadline directly from the reviewed artifact.
- OCR-derived text egress and ordinary bounded clipboard movement stay aligned with the rest of the explicit-crossing model.

### Negative
- Implementations have to publish one exact deadline field instead of relying on soft timeout conventions.
- Late paste attempts that might have worked under broker-specific grace periods now fail closed and require a fresh grant.

## Alternatives considered

- **Keep deriving lifetime from `ttl_seconds` and `expires_at`:** too much room for implementation drift.
- **Allow broker grace periods after expiry:** silently widens authority past the reviewed artifact.
- **Design a fuller retry/renewal subsystem now:** too large for this iteration; the smaller useful cut is to make the deadline exact.

## References / affected docs
- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`
