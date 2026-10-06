# Packet-capture stronger export remote reverification boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md` already fixed the question “can operators find the same accepted remote object again?”
This doc fixes the next narrower question:
**can DeriveBSD re-check that accepted remote object later without re-downloading packet bytes or hand-auditing portal UI state?**

See also:
- ADR: `adrs/ADR-0115-packet-capture-strong-export-remote-reverification-boundary.md`
- packet-capture stronger export remote-locator continuity boundary: `docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`
- policy-constrained transports: `docs/255-policy-constrained-transports.md`
- transport reverification receipt: `spec/transport.reverification.receipt.schema.json`
- packet-capture export transport reverification receipt profile: `spec/packet.capture.export.transport.reverification.receipt.profile.schema.json`

## Why this needs a hard decision

The archive already says canonical stronger packet export must keep the same:

- approved destination tuple,
- normalized artifact digest,
- remote object id,
- remote representation/version validator,
- recipient-side protection posture,
- and recipient-side locator.

But one narrow ambiguity still remained.
A team could later say “yes, that accepted remote object still exists” while proving it only by screenshots, portal clicking, or by downloading the stronger raw bytes all over again.
That is too loose for canonical follow-up evidence, especially in A and D where later support, incident, or regulatory review wants a receipted re-check rather than operator folklore.

## Accepted boundary

Across all profiles:

- `packet.capture.summary` remains the ordinary export class,
- `packet.capture.normalized` remains the stronger explicit raw-byte class,
- the stronger export still completes at recipient acceptance,
- but later remote evidence checks now have an official typed follow-up lane too.

That lane is `transport.reverification.receipt`, specialized for stronger packet export by `packet.capture.export.transport.reverification.receipt.profile`.

The canonical rule is deliberately narrow:

- re-verification is **metadata-first**,
- `reverification.body_downloaded = false`,
- and the packet-specific reverification receipt must stay aligned with the same accepted stronger object.

## Canonical remote reverification rule

When `artifact.kind = packet.capture.normalized`, canonical stronger packet reverification now requires all of the following:

- `transport.reverification.receipt.export_receipt_digest`
- `transport.reverification.receipt.transport_acceptance_receipt_digest`
- `transport.reverification.receipt.reverification.body_downloaded = false`
- `transport.reverification.receipt.reverification.status = match`
- `transport.reverification.receipt.reverification.remote_validator`
- `transport.reverification.receipt.reverification.remote_protection`
- `transport.reverification.receipt.reverification.remote_locator`

The hard decision is not merely that these fields exist.
The hard decision is that later re-checks should remain about the **same accepted remote packet object** while using metadata-only probes instead of packet-body re-download or portal screenshots.

So the stronger packet story is now:

1. the same recipient was approved,
2. the same normalized bytes were exported,
3. the same remote object id / validator / protection posture / locator were preserved,
4. and later evidence re-check can be receipted as a metadata-only reverification of that same accepted remote object.

## Why this is the right coherence cut

This is still a small rule.
It does **not** standardize one provider-specific API.
It simply says the stronger packet-export lane should not call later remote evidence checks “good enough” when they depend on UI clicking or another raw-byte download.

That keeps A–D coherent without forks:

- A gets metadata-only reverification for fleet/vendor incident follow-up,
- B keeps humane support workflows because the same receipt can be produced from ticket metadata rather than packet-body replay,
- C keeps compatibility adapters viable by allowing generic method kinds,
- D gets a typed remote evidence re-check shape for audits and regulatory reviews.

## Research note

HTTP already distinguishes metadata-first checks from full-body transfer, and common object/ticket storage systems expose metadata lookup operations too.
DeriveBSD should keep the same lesson in the stronger packet-export lane: later confidence checks should be receipted as **metadata-only reverification** where possible, not reconstructed from downloads or screenshots.

Last updated: 2026-03-09r254
