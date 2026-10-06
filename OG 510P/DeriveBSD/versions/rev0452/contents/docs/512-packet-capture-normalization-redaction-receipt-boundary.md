# Packet-capture normalization redaction-receipt boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain  
**Patterns:** Plan→Apply→Receipt, Bundles  

`docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md` already decided that stronger packet-capture artifacts enter through the typed safe-open import lane and normalize before ordinary promotion/export.
This doc fixes the next small but expensive question:
**what evidence makes a normalized packet-capture derivative real enough to trust?**

See also:
- ADR: `adrs/ADR-0102-packet-capture-normalization-redaction-receipt-boundary.md`
- strong-artifact intake boundary: `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`
- deterministic redaction transforms: `docs/195-deterministic-redaction-transforms.md`
- packet-capture export posture: `docs/251-export-policies-and-support-bundle-portal.md`
- stronger packet-capture export proof boundary: `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`
- canonical packet-capture import profile: `spec/content.import.packet-capture.receipt.schema.json`
- canonical packet-capture normalization profiles: `spec/redaction.transform.packet-capture.schema.json`, `spec/redaction.receipt.packet-capture.schema.json`

## Why this needs a hard decision

`strip-metadata` is not enough as a verbal promise.
If the archive stops there, packet-capture normalization becomes a hidden tool side effect:

- the import receipt says a derived file exists, but not which deterministic sanitization policy produced it,
- export/support review cannot tell whether the derivative is actually `packet-records-only`,
- and packet-capture cleanup drifts away from the redaction machinery that the rest of DeriveBSD already uses for privacy-preserving evidence.

DeriveBSD already has a general answer to this shape of problem:
**deterministic redaction transforms plus redaction receipts.**
Packet capture should reuse that answer instead of inventing a packet-specific proof vocabulary.

## Accepted boundary

Across all profiles:

- stronger packet-capture artifacts still enter on `content.import.plan` / `content.import.receipt`,
- the original imported strong artifact remains quarantined evidence,
- any normalized derivative that is meant to become an ordinary review/export candidate must bind to generic redaction evidence,
- the canonical transform is a constrained `redaction-transform` profile for `pcap`,
- the canonical proof is a constrained `redaction-receipt` profile,
- and `content.import.packet-capture.receipt` must point at that redaction evidence through typed normalized-output labels on the derived artifact it emits.

This keeps the packet-capture lane coherent with the archive’s existing redaction/evidence story.

## Canonical typed shapes

The archive now carries three connected typed surfaces:

- `spec/content.import.packet-capture.receipt.schema.json`
- `spec/redaction.transform.packet-capture.schema.json`
- `spec/redaction.receipt.packet-capture.schema.json`

The important constraint is that the packet-capture profiles **do not replace** the generic kinds.
They stay constrained profiles over:

- `kind = content.import.receipt`
- `kind = redaction-transform`
- `kind = redaction-receipt`

The archive therefore keeps one redaction vocabulary across logs, traces, bundles, and packet-capture normalization.

## Normalize-to-redaction proof rule

The narrow hard decision is:
**a normalized packet-capture derivative is not an ordinary promotion candidate unless a generic redaction receipt proves how it was derived.**

In practice, the typed packet-capture import receipt must annotate the normalized derived output with:

- `redaction_transform_digest`
- `redaction_receipt_digest`
- `promotion_verdict`
- `metadata_posture = packet-records-only`

The normalized output digest itself remains the join key back to the generic redaction receipt.
That makes “normalized packet capture” a queryable, reviewable fact rather than a filename convention.

## Allowlist-first posture

The official normalization posture is conservative:

- keep packet records and the framing needed to parse them,
- keep the summary/export story centered on `packet.capture.summary`,
- strip stronger sideband metadata such as capture comments, packet comments, name-resolution material, decryption-secret blocks, and other non-authoritative sideband metadata,
- and mark the result `summary-only` rather than ordinary-export-eligible if the transform cannot produce a clean `packet-records-only` derivative.

This is the same design instinct already used elsewhere in the archive:
prefer an explicit allowlist over vague “sanitize whatever looks risky” folklore.

## Product-shape defaults

| Profile | Default normalization proof posture | Practical meaning |
|---|---|---|
| **A fleet_host** | `safe-open + redaction-receipt-required` | Stronger capture review stays operational, but promotion/export needs deterministic proof of the sanitization step. |
| **B workstation** | `trusted-ui-visible safe-open + redaction-receipt-required` | Local troubleshooting can still happen, but richer packet files only become ordinary share objects after typed normalization evidence exists. |
| **C general_os** | `compatibility adapters allowed, official lane requires redaction proof` | Tools can vary, but the archive still has one official proof shape for supportable workflows. |
| **D appliance_factory** | `safe-open-only + strongest proof posture` | Regulatory/appliance workflows can inspect risky captures, but any derived exportable artifact must carry deterministic sanitization evidence. |

## Review guidance

When reviewing packet-capture normalization, ask:

1. Did the stronger artifact stay on `content.import.*` rather than becoming host-open folklore?
2. Does the import receipt point at a generic `redaction-transform` + `redaction-receipt` rather than only saying `strip-metadata` happened?
3. Is the normalized output digest the same digest referenced by the redaction receipt?
4. Does the redaction proof explicitly end at `output_metadata_posture = packet-records-only` or else force `summary-only`?
5. Is the original stronger artifact still quarantined instead of silently becoming the ordinary support/export payload?

## Why this is worth locking now

This is not a new packet-analysis stack.
It is a small coherence cut that joins three things the archive already wants:

- stronger packet captures must safe-open,
- ordinary review/export should prefer typed summaries or normalized derivatives,
- and deterministic privacy filtering should already produce reusable evidence.

Locking that join now makes later implementation work cheaper:

- A keeps incident response explainable,
- B keeps local troubleshooting visible without ambient risky files,
- C keeps compatibility tools adapter-shaped,
- D keeps the appliance/regulatory story auditable.

Last updated: 2026-03-09r243
