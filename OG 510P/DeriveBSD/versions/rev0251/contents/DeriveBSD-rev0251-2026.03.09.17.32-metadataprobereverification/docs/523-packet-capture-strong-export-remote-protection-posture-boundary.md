# Packet-capture stronger export remote-protection posture boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md` already fixed the question “was this the same remote representation/version?”
This doc fixes the next narrower question:
**did the recipient-side lane say anything typed about overwrite/delete resistance for that accepted representation, or are we still calling a transient upload ‘durable evidence’?**

The next narrower retrieval/discoverability cut now lives in `docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`, because a protected remote copy is still operationally weak if later evidence retrieval falls back to portal folklore.

See also:
- ADR: `adrs/ADR-0113-packet-capture-strong-export-remote-protection-posture-boundary.md`
- packet-capture stronger export remote-validator continuity boundary: `docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`
- policy-constrained transports: `docs/255-policy-constrained-transports.md`
- packet-capture export transport acceptance receipt profile: `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`
- packet-capture export receipt profile: `spec/packet.capture.export.receipt.profile.schema.json`

## Why this needs a hard decision

The archive already says canonical stronger packet export must keep the same:

- approved destination tuple,
- normalized artifact digest,
- remote object id,
- remote representation/version validator,
- and recipient-side acceptance.

But one narrow ambiguity still remained.
A recipient lane can truthfully say “yes, the right bytes landed here” while still giving DeriveBSD no typed answer about whether the accepted copy is protected from later overwrite or routine deletion.
That is too loose for canonical stronger raw-byte export, especially for fleet-host and appliance/regulatory shapes.

## Accepted boundary

Across all profiles:

- `packet.capture.summary` remains the ordinary export class,
- `packet.capture.normalized` remains the stronger explicit raw-byte class,
- stronger raw-byte export still reuses the generic transport-acceptance and export receipts,
- but canonical stronger packet export is now **remote-protection-shaped** too.

This means the stronger proof chain must keep one aligned `remote_protection` object through:

- `transport.acceptance.receipt.acceptance.remote_protection`
- `export.receipt.adapter.remote_protection`

The posture stays intentionally generic so one archive rule can cover multiple adapters.
The `mode` may be:

- `versioned-noncurrent-retained`
- `retain-until`
- `policy-locked-retention`
- `legal-hold`
- `append-only-log`
- `opaque-reviewed`

For `retain-until` and `policy-locked-retention`, `retain_until` is required so the archive can say how long the recipient-side protection window was supposed to last.

## Canonical remote-protection continuity rule

When `artifact.kind = packet.capture.normalized`, canonical stronger export now requires all of the following:

- `transport.acceptance.receipt.acceptance.remote_protection.mode`
- `export.receipt.adapter.remote_protection.mode`
- and, when present, aligned `retain_until` / note fields describing the same recipient-side protection claim.

The hard decision is not merely that these fields exist.
The hard decision is that they stay on the **same remote protection posture** across recipient acceptance and final export evidence.

So the stronger packet story is now:

1. the same recipient was approved,
2. the same normalized bytes were exported,
3. the same remote object id was used,
4. the same remote representation/version validator was observed,
5. and the recipient-side lane made one explicit claim about overwrite/delete resistance for that same accepted representation.

## Why this is the right coherence cut

This is still a small rule.
It does **not** standardize one provider-specific evidence store.
It simply says the stronger packet-export lane should not call the remote copy “durable evidence” unless the recipient-side proof chain says what kind of overwrite/delete resistance it has.

That keeps A–D coherent without forks:

- A keeps vendor escalation evidence pinned to a named remote protection posture rather than “the ticket system probably keeps it,”
- B keeps explicit support sharing viable while making durability claims honest instead of ambient,
- C keeps compatibility adapters viable by permitting `opaque-reviewed` when that is all they can honestly surface,
- D gets a typed place to express hold/retention-lock/append-only recipient posture for factory or regulatory lanes.

## Research note

Current mainstream object stores already expose this distinction in different words.
AWS S3 Object Lock separates retention periods from legal holds.
Azure immutable blob storage documents time-based retention policies and legal holds as WORM posture.
Google Cloud Storage documents locked retention policies and object retention lock as ways to prevent early removal or replacement.
DeriveBSD does not copy any one provider API, but the stronger packet-export lane should steal the lesson: recipient acceptance alone is not enough to claim durable evidence when the remote side can also describe protection against overwrite/delete.

Last updated: 2026-03-09r253
