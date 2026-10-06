# Event journal digests stay chain-exact and seal-list-bound

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain, reproducibility  
**Patterns:** Plan→Apply→Receipt, Bundles  

DeriveBSD already wanted the event journal to be more than a string pile.
This doc fixes the smaller but implementation-shaping question the archive had left vague:

**what exact digest rules make `event.record`, `event.segment`, and `event.seal.receipt` mechanically verifiable?**

This is intentionally not a new subsystem and not a new product-profile key.
It is the missing exactness boundary for the existing local event lane.

See also:
- ADR: `adrs/ADR-0213-event-journal-digests-stay-chain-exact-and-seal-list-bound.md`
- structured event journal: `docs/215-structured-event-log-as-evidence.md`
- sealing lane: `docs/424-forward-secure-event-log-sealing.md`
- support-bundle join: `docs/625-incident-bundles-carry-event-seal-proof-by-digest.md`
- evidence spine: `docs/229-evidence-spine-overview.md`

## Why this needs a hard decision

The archive already said the right things conceptually:

- `event.record` could chain through `prev_digest`,
- `event.segment` could bind file bytes plus continuity metadata,
- and `event.seal.receipt` could seal ordered segment sets.

But the exact digest rules were still implied instead of fixed.
That is expensive because it lets different implementations all claim they are emitting “event proof” while computing different digests.
The canonical examples made that worse by still using placeholders for the chain itself.

A coherent archive needs one boring answer for the event lane, because this is exactly the evidence people reach for when everything else is on fire.

## Accepted boundary

### 1) Record chaining is digest-of-record, not id folklore

`event.record.prev_digest` now means:

- take the previous `event.record` object exactly as stored,
- JCS-canonicalize it,
- hash the UTF-8 bytes with `sha256`,
- store the result as `sha256:<hex>`.

That keeps record continuity bound to content instead of only to a UUID or an implementation-private cursor.

### 2) Segment file identity is exact-byte identity

`event.segment.file_digest` is the digest of the exact segment blob bytes.
The archive does not require one universal blob encoding, but whatever bytes the segment stores are the bytes the digest covers.

The canonical example intentionally uses an uncompressed `jsonl` blob so the proof chain is easy to inspect:

- companion blob: `spec/examples/event.segment.host-host-4f2a.seg-000001.jsonl`
- metadata object: `spec/examples/event.segment.json`

### 3) Merkle roots bind ordered record content digests

When `merkle_root_digest` is present, it is the sha256 Merkle root over the ordered per-record content digests for that segment.
Each leaf is `sha256(utf8(JCS(event_record)))` for the record exactly as stored.
Odd levels duplicate the final leaf.

This keeps segment-level integrity proof about ordered record content, not about formatter folklore.

### 4) Segment chain heads bind continuity metadata exactly

`event.segment.chain_head_digest` is the continuity digest for the segment lane. When `chain_head_digest` is present, compute it as `sha256(utf8(JCS(chain_envelope)))` where `chain_envelope` contains:

- `stream_id`
- `segment_id`
- `file_digest`
- `count`
- `first_at`
- `last_at`
- `merkle_root_digest` when present
- `prev_chain_head_digest` when present

This is the official continuity head for the segment lane.
It is deliberately small: enough to prove segment ordering/integrity without inventing a second giant journal-manifest object.

### 5) Seal roots commit to an exact ordered segment list

`event.seal.receipt.segments_root_digest` is now the digest of an exact ordered list, not an open-ended “some root somehow” field.
Compute it as:

- `sha256(utf8(JCS({"stream_id": receipt.stream_id, "segments": [{"segment_id","file_digest"}, ...]})))`

When `seal.segments[]` is present, that list is the exact committed list.
`first_segment_id`, `last_segment_id`, and `segment_count` summarize the set, but they do not replace the ordered commitment.

This keeps the sealing lane closer to CloudTrail-style ordered digest files than to implementation-private batch folklore, while still fitting DeriveBSD's digest-first evidence model. See AWS CloudTrail digest file structure and integrity-validation overview: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-digest-file-structure.html and https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html

## Canonical example chain

The archive now carries one fully checkable mini-chain:

1. `spec/examples/event.segment.host-host-4f2a.seg-000001.jsonl` contains the exact segment blob bytes.
2. `spec/examples/event.record.json` matches the second record in that segment and carries the exact `prev_digest` of the first record.
3. `spec/examples/event.segment.json` binds the exact segment `file_digest`, the exact ordered-record `merkle_root_digest`, and the exact `chain_head_digest`.
4. `spec/examples/event.seal.receipt.json` seals the exact ordered segment list through `segments_root_digest`.

That chain is now guarded in CI instead of being left to prose.

## Practical meaning

### A / fleet host and D / appliance-regulatory

These shapes are the ones most likely to need auditable “prove the evidence store was not silently rewritten” answers.
The archive does not force sealing on every deployment, but when these lanes are enabled, the digest rules are now exact.

### B / workstation

B still keeps evidence export and richer collection profile-shaped.
This boundary does not add ambient logging; it only makes the existing typed event lane checkable when it exists.

### C / general-purpose OS

C keeps compatibility options real.
This boundary prevents “works with journald/syslog/adapter X” from quietly becoming “the event-proof story is whatever adapter X happened to hash.”

## Guardrail

- `tools/check_event_journal_digest_contract.py`

The guardrail verifies the companion segment blob, record-chain digest, segment Merkle/root/head digests, and sealing root from the canonical examples.
If this check fails, the archive is drifting away from its own event-proof story.

## What remains open

This doc does **not** fix:

- the final journal storage backend,
- the final segment-rotation cadence,
- the final sealing-key ceremony,
- or whether richer remote collectors/verifiers exist.

The expensive hard decision is smaller:
DeriveBSD now has one exact digest recipe for its local event journal lane.

Last updated: 2026-03-21r355
