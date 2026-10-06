# ADR-0250: Workstation single-delivery data-transfer grants stay one-shot and fresh-grant-required

## Status
Accepted

## Context

`adrs/ADR-0128-workstation-cross-domain-datatransfer-floor.md` already fixed the ordinary workstation data-transfer posture: explicit cross-domain transfer, no ambient shared clipboard, and `single-delivery` as the boring default. `ADR-0248` then made the actor pair exact (`offer_source_subject` + `subject`), and `ADR-0249` made receipts joinable back to the exact `ui.datatransfer.grant` artifact through `grant_digest`.

One small but still practical ambiguity remained:
**what exactly happens to an ordinary single-delivery grant after the first successful read-side transfer?**

If the archive leaves that fuzzy, implementations can drift toward replay folklore:

- hidden broker re-delivery when a destination app later claims the paste failed,
- host clipboard history resurrecting a spent cross-domain transfer,
- or support/export tooling guessing whether another read under the same `offer_id` was still in policy.

## Decision

For the ordinary workstation lane:

1. `delivery_mode = single-delivery` means one successful read-side delivery under that exact grant artifact.
2. The first successful read-side transfer exhausts the grant.
3. Successful ordinary read-side receipts must therefore carry `grant_exhausted = true`.
4. Ordinary recovery after that point is a **fresh explicit grant / re-offer**, not replay of the spent grant.
5. Clipboard history resurrection, broker-memory replay, and stale `offer_id` reuse are not baseline interpretations of `single-delivery`.

## Consequences

### Positive
- `single-delivery` becomes operationally exact rather than rhetorical.
- OCR-derived text egress stays bounded all the way through: explicit, plain-text, actor-exact, exact-grant-joined, and one-shot.
- Any future richer lane now has to identify itself explicitly as a multi-delivery/history exception instead of piggybacking on the ordinary baseline.

### Negative
- Destinations that lose pasted text after a successful transfer cannot rely on implicit replay; users or tooling must explicitly re-offer.
- Implementations need to preserve the exact ordinary meaning of `grant_exhausted` rather than treating it as optional convenience metadata.

## Alternatives considered

- **Let brokers decide replay behavior locally:** too much implementation drift for a lane that is supposed to be boring and supportable.
- **Treat clipboard history as ordinary recovery:** silently recreates ambient cross-domain state.
- **Design the full multi-delivery/history subsystem now:** too large for this iteration; the ordinary one-shot meaning is the smaller useful cut.

## References / affected docs
- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`
- `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`
