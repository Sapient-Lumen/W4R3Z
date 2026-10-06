# Packet-capture stronger export remote-validator continuity boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md` already fixed the question “was this the same remote object id?”
This doc fixes the next narrower question:
**if that remote object id can expose a stronger representation/version validator, does the stronger proof chain keep that validator aligned too?**

See also:
- ADR: `adrs/ADR-0112-packet-capture-strong-export-remote-validator-continuity-boundary.md`
- packet-capture stronger export remote-object continuity boundary: `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`
- policy-constrained transports: `docs/255-policy-constrained-transports.md`
- packet-capture export transport receipt profile: `spec/packet.capture.export.transport.receipt.profile.schema.json`
- packet-capture export transport acceptance receipt profile: `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`
- packet-capture export receipt profile: `spec/packet.capture.export.receipt.profile.schema.json`

## Why this needs a hard decision

The archive already says canonical stronger packet export must keep the same:

- approved destination tuple,
- normalized artifact digest,
- recipient-side acceptance,
- and remote object id.

But one narrow ambiguity still remained.
A remote system can expose a stable object handle **and** a stronger representation/version validator for the bytes currently stored behind that handle.
If DeriveBSD ignores that validator, the stronger proof chain can still collapse back to:

- “the same case/ticket/object id was involved”,
- even though the remote system itself has a better answer for “which stored representation/version was accepted?”.

That is too loose for canonical stronger raw-byte export.

## Accepted boundary

Across all profiles:

- `packet.capture.summary` remains the ordinary export class,
- `packet.capture.normalized` remains the stronger explicit raw-byte class,
- stronger raw-byte export still reuses the generic transport / acceptance / export receipts,
- but canonical stronger packet export is now **remote-validator-continuous** too.

This means the stronger proof chain must keep the same remote validator/revision token through:

- `transport.receipt.result.remote_validator`
- `transport.acceptance.receipt.acceptance.remote_validator`
- `export.receipt.adapter.remote_validator`

The validator stays intentionally generic so one archive rule can cover multiple adapters.
The `kind` may be `etag-strong`, `etag-weak`, `version-id`, `attachment-revision`, `message-id`, or another `opaque` revision token.

## Canonical remote-validator continuity rule

When `artifact.kind = packet.capture.normalized`, canonical stronger export now requires all of the following:

- `transport.receipt.result.remote_validator.kind`
- `transport.receipt.result.remote_validator.value`
- `transport.acceptance.receipt.acceptance.remote_validator.kind`
- `transport.acceptance.receipt.acceptance.remote_validator.value`
- `export.receipt.adapter.remote_validator.kind`
- `export.receipt.adapter.remote_validator.value`

And the hard decision is not that these fields merely exist.
The hard decision is that they stay on the **same remote validator** across transport, recipient acceptance, and final export evidence.

So the stronger packet story is now:

1. the same recipient was approved,
2. the same normalized bytes were exported,
3. the same remote object id was used,
4. and the same remote representation/version validator was observed the whole way through.

## Why this is the right coherence cut

This is still a small rule.
It does **not** standardize one provider-specific revision model.
It simply says the stronger packet-export lane should preserve the strongest remote representation handle the adapter already knows.
The next closure cut then asks whether that accepted remote representation was also described with a typed overwrite or routine deletion resistance posture (`docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`).

That keeps A–D coherent without forks:

- A keeps vendor escalations pinned to one receipted remote representation/version instead of a mutable portal narrative,
- B keeps stronger support sharing reviewable even when a helpdesk mutates attachment handles in place,
- C keeps compatibility adapters viable by accepting opaque revision tokens when that is all they can surface,
- D gets a tighter dossier story when regulator/factory evidence leaves the trust boundary.

## Research note

HTTP already treats `ETag` as an opaque validator for differentiating multiple representations of the same resource, and RFC 9110 explicitly says such validators can be based on internal revision numbers or other implementation-specific versioning.
AS2 receipt practice makes the same general point from another angle: keep correlation handles plus integrity evidence together when proving remote receipt.
DeriveBSD does not copy those wire formats, but the stronger packet-export lane should keep the same discipline: if the adapter can see a remote representation/version validator, preserve it in the proof chain instead of collapsing back to object id alone.

Last updated: 2026-03-09r252
