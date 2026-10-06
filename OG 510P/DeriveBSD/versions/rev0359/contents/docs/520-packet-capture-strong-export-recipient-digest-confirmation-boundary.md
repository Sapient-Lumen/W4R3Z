# Packet-capture stronger export recipient-digest confirmation boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/517-packet-capture-strong-export-digest-stability-boundary.md` already kept the stronger chain on the same normalized digest locally.
`docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md` then separated recipient acceptance from mere send success, and `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md` kept that stronger act tied to the approved destination tuple.
This doc fixes the remaining remote-side ambiguity:
**what proves the recipient accepted this exact normalized artifact rather than merely some plausible object at the same destination?**

See also:
- ADR: `adrs/ADR-0110-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`
- packet-capture stronger export digest-stability boundary: `docs/517-packet-capture-strong-export-digest-stability-boundary.md`
- packet-capture stronger export recipient-acceptance boundary: `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`
- packet-capture stronger export destination-bound approval boundary: `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`
- packet-capture stronger export remote-object continuity boundary: `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`
- policy-constrained transports: `docs/255-policy-constrained-transports.md`
- packet-capture export transport acceptance receipt profile: `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`
- packet-capture export receipt profile: `spec/packet.capture.export.receipt.profile.schema.json`

## Why this needs a hard decision

The archive already says stronger packet export must be:

- normalized before ordinary promotion,
- explicitly approved by a real actor,
- destination-bound to the approved recipient tuple,
- transported through a policy-bound handoff lane,
- digest-stable across local normalization, approval, transport, acceptance, and export,
- and final only once the recipient-side lane accepted the artifact.

But one expensive ambiguity still remained:

- `transport.acceptance.receipt` could prove that the intended recipient lane accepted *something*,
- the stronger chain could still be locally digest-stable,
- yet the recipient-side receipt still might not echo back the identity of the exact artifact it accepted.

That is too weak.
A stronger raw-byte export needs a typed answer to **did the recipient accept this exact normalized capture?**

## Accepted boundary

Across all profiles:

- `packet.capture.summary` remains the ordinary export class,
- `packet.capture.normalized` remains the stronger explicit raw-byte class,
- stronger raw-byte export still reuses the generic `transport.acceptance.receipt` substrate,
- but stronger recipient acceptance is now **digest-confirming** as well as recipient-bound.

This means DeriveBSD does **not** invent a packet-capture-only remote attestation service.
Instead, it fixes one narrow extra rule on the existing acceptance lane:
**a canonical stronger packet acceptance receipt must echo the same normalized digest through `acceptance.remote_artifact_digest`.**

## Canonical typed acceptance confirmation rule

The packet-capture transport-acceptance profile now requires all of the following for stronger `packet.capture.normalized` export:

- `artifact.kind = packet.capture.normalized`
- `outcome = accepted`
- `acceptance.remote_reference`
- `acceptance.accepted_at`
- `acceptance.remote_artifact_digest`

The hard decision is not merely that a remote digest may be present.
The hard decision is that stronger packet export only reaches canonical recipient acceptance when that remote digest equals the same normalized digest already carried by:

1. `redaction.receipt.output_digest`
2. `consent.request.action.artifact_digest`
3. `transport.receipt.artifact.digest`
4. `transport.acceptance.receipt.artifact.digest`
5. `transport.acceptance.receipt.acceptance.remote_artifact_digest`
6. `export.receipt.artifact.digest`

That keeps the stronger chain honest about both recipient continuity and remote-side byte continuity.
The next cut after this then keeps the chain on the same remote object id too, so transport / recipient acceptance / final export evidence do not quietly drift across multiple attachments in the same case (`docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`).

## Why this is the right coherence cut

This is deliberately narrow.
It does **not** require every recipient system to expose fancy attestation APIs.
It only says that if a system cannot echo back the accepted artifact digest, then it is not good enough for canonical stronger `packet.capture.normalized` acceptance.

That keeps A–D coherent without forks:

- A keeps vendor escalations bound to the exact normalized capture the vendor-side lane surfaced,
- B keeps trusted-UI-visible stronger sharing honest about whether the recipient-side system really accepted the same artifact,
- C keeps compatibility adapters possible, but only if they can recover or compute a digest-confirming receipt,
- D keeps appliance/regulatory exports tight enough for later dossier correlation and audit.

## Research note

This boundary borrows a practical lesson from receipt systems that distinguish mere visibility from content-confirming receipt.
AS2 signed receipts include a Received-content-MIC specifically so the stronger receipt can confirm the content that was received rather than just the fact that some message was processed.
DeriveBSD does not copy AS2’s wire format, but the stronger packet-export lane should keep the same discipline: recipient acceptance should confirm the same artifact digest, not merely the same ticket or recipient tuple.

Last updated: 2026-03-09r250