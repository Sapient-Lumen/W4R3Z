# Packet-capture stronger export remote-object continuity boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md` already kept stronger packet export tied to the approved destination tuple.
`docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md` then kept recipient acceptance on the same normalized digest.
This doc fixes the remaining remote-side object ambiguity:
**what proves transport, recipient acceptance, and final export evidence are all talking about the same remote object id rather than different objects inside the same case?**

See also:
- ADR: `adrs/ADR-0111-packet-capture-strong-export-remote-object-continuity-boundary.md`
- packet-capture stronger export destination-bound approval boundary: `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`
- packet-capture stronger export recipient-digest confirmation boundary: `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`
- policy-constrained transports: `docs/255-policy-constrained-transports.md`
- packet-capture export transport receipt profile: `spec/packet.capture.export.transport.receipt.profile.schema.json`
- packet-capture export transport acceptance receipt profile: `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`
- packet-capture export receipt profile: `spec/packet.capture.export.receipt.profile.schema.json`

## Why this needs a hard decision

The archive already says stronger packet export must be:

- destination-bound to the approved recipient tuple,
- digest-confirming on the same normalized artifact,
- and final only once recipient acceptance exists.

But one narrow ambiguity still remained:

- `transport.receipt.result.remote_id` could name one remote attachment/object,
- `transport.acceptance.receipt.acceptance.remote_reference` could name some plausible object in the same case,
- `export.receipt` could then close the act without naming which remote object survived,
- and the whole chain would still look locally coherent.

That is still too weak for canonical stronger raw-byte export.
A stronger packet handoff needs a typed answer to **did the same remote object id survive transport, recipient acceptance, and final export evidence?**

## Accepted boundary

Across all profiles:

- `packet.capture.summary` remains the ordinary export class,
- `packet.capture.normalized` remains the stronger explicit raw-byte class,
- stronger raw-byte export still reuses the generic transport / acceptance / export receipts,
- but stronger packet export is now **remote-object-continuous** as well as destination-bound and digest-confirming.

This means DeriveBSD does **not** invent a packet-only portal protocol.
Instead it fixes one narrow extra rule on the existing proof chain:
**when the adapter exposes a stable remote object id, canonical stronger packet export must keep that same id through `transport.receipt.result.remote_id`, `transport.acceptance.receipt.acceptance.remote_reference`, and `export.receipt.adapter.remote_id`.**

## Canonical remote-object continuity rule

The packet-capture stronger-export chain now requires all of the following when `artifact.kind = packet.capture.normalized`:

- `transport.receipt.result.remote_id`
- `transport.acceptance.receipt.acceptance.remote_reference`
- `export.receipt.adapter.remote_id`

The hard decision is not merely that these fields may exist.
The hard decision is that canonical stronger packet export only closes when those three fields stay on the **same remote object identifier**.

That keeps the stronger chain honest about:

1. which recipient got the artifact,
2. which bytes were accepted,
3. and which exact remote attachment/message/object id the recipient-side lane actually ended up using.

## Why this is the right coherence cut

This is deliberately small.
It does **not** require a universal remote object taxonomy.
It only says that if an adapter claims a stable remote object id, then the canonical stronger proof chain must keep that id aligned end-to-end.

That keeps A–D coherent without forks:

- A keeps vendor escalations correlated to one receipted remote attachment id rather than a fuzzy case narrative,
- B keeps stronger user-approved sharing reviewable when a portal or ticket system mutates object references,
- C keeps compatibility adapters viable, but only if they can surface one stable remote object id,
- D keeps dossier and regulator handoff stories tighter by binding bytes, recipient, and remote object together.

## Research note

This boundary borrows a practical lesson from receipt systems that preserve correlation handles across transport and stronger receipt evidence.
MDN prior art explicitly preserves `Original-Message-ID` so disposition reports can be correlated to the original message on a per-recipient basis, and AS2 receipts likewise keep message identifiers plus a MIC together when proving receipt.
DeriveBSD does not copy those wire formats, but the stronger packet-export lane should keep the same discipline: the final proof chain should preserve one stable remote object id instead of letting “some object in the same case” stand in for the actual accepted attachment. That still is not the whole story when the adapter exposes a stronger revision/representation validator, which is why the next boundary pins `remote_validator` continuity too (`docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`) and keeps the same remote validator aligned when the adapter can see one.

Last updated: 2026-03-09r251