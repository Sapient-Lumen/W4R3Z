# Packet-capture stronger export remote-locator continuity boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md` already fixed the question “did the recipient-side lane say anything typed about durability?”
This doc fixes the next narrower question:
**can DeriveBSD still point operators at the same remote object later, or are we back to portal folklore and ticket clicking?**

See also:
- ADR: `adrs/ADR-0114-packet-capture-strong-export-remote-locator-continuity-boundary.md`
- packet-capture stronger export remote-protection posture boundary: `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`
- policy-constrained transports: `docs/255-policy-constrained-transports.md`
- packet-capture export transport receipt profile: `spec/packet.capture.export.transport.receipt.profile.schema.json`
- packet-capture export transport acceptance receipt profile: `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`
- packet-capture export receipt profile: `spec/packet.capture.export.receipt.profile.schema.json`

## Why this needs a hard decision

The archive already says canonical stronger packet export must keep the same:

- approved destination tuple,
- normalized artifact digest,
- remote object id,
- remote representation/version validator,
- recipient-side acceptance,
- and recipient-side protection posture.

But one narrow ambiguity still remained.
A recipient lane can truthfully say “yes, the right bytes landed here and the copy is protected this way” while still giving DeriveBSD no stable typed locator for finding that same remote object again later.
That is too loose for canonical stronger raw-byte export, especially when support and regulated workflows need later review, retrieval, or evidence re-check without provider-specific guesswork.

## Accepted boundary

Across all profiles:

- `packet.capture.summary` remains the ordinary export class,
- `packet.capture.normalized` remains the stronger explicit raw-byte class,
- stronger raw-byte export still reuses the generic transport, transport-acceptance, and export receipts,
- but canonical stronger packet export is now **remote-locator-continuous** too.

This means the stronger proof chain must keep one aligned `remote_locator` object through:

- `transport.receipt.result.remote_locator`
- `transport.acceptance.receipt.acceptance.remote_locator`
- `export.receipt.adapter.remote_locator`

The locator stays intentionally generic so one archive rule can cover multiple adapters.
The `kind` may be:

- `uri-hint`
- `ticket-attachment`
- `portal-object`
- `message-part`
- `object-path`
- `opaque`

The locator value must be redacted/non-secret.
It is not an authority token; it is a typed discoverability handle for the already-approved stronger handoff.
And once later follow-up needs to re-check that same accepted object, the archive now expects typed metadata-only reverification rather than portal folklore (`docs/525-packet-capture-strong-export-remote-reverification-boundary.md`).

## Canonical remote-locator continuity rule

When `artifact.kind = packet.capture.normalized`, canonical stronger export now requires all of the following:

- `transport.receipt.result.remote_locator`
- `transport.acceptance.receipt.acceptance.remote_locator`
- `export.receipt.adapter.remote_locator`

The hard decision is not merely that these fields exist.
The hard decision is that they stay on the **same remote locator** across transport, recipient acceptance, and final export evidence.

So the stronger packet story is now:

1. the same recipient was approved,
2. the same normalized bytes were exported,
3. the same remote object id was used,
4. the same remote representation/version validator was observed,
5. the same remote protection posture was claimed,
6. and the same recipient-side locator remained available for later evidence retrieval/review of that same object.

## Why this is the right coherence cut

This is still a small rule.
It does **not** standardize one provider-specific retrieval API.
It simply says the stronger packet-export lane should not call the remote copy “canonical completed handoff” while leaving later discoverability to portal folklore.

That keeps A–D coherent without forks:

- A keeps vendor escalation evidence retrievable by a typed locator rather than “the operator can probably find it again,”
- B keeps explicit support sharing viable while preserving a humane, receipted breadcrumb back to the accepted object,
- C keeps compatibility adapters viable by permitting `opaque` when that is all they can honestly surface,
- D gets a typed place to preserve case/object discoverability for audits and factory/regulatory evidence review.

## Research note

The archive already uses redacted `uri_hint` fields on destinations because operators need non-secret discoverability breadcrumbs even when the hint is not itself the authority.
The stronger packet-export lane should keep the same lesson on the recipient side too: durable evidence is much easier to verify when the proof chain also preserves a stable typed locator for finding the accepted remote object again later.

Last updated: 2026-03-09r254
