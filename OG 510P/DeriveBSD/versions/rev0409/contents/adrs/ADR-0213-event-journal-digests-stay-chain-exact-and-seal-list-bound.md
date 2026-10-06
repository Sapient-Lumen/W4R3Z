# ADR-0213: Event journal digests stay chain-exact and seal-list-bound

- Status: Accepted
- Date: 2026-03-21

## Context

DeriveBSD already treats local events as typed evidence (`event.record`, `event.segment`, and optional `event.seal.receipt`).
`docs/215-structured-event-log-as-evidence.md` and `docs/424-forward-secure-event-log-sealing.md` already had the right shape conceptually too:

- records can chain through `prev_digest`,
- segments can prove bounded integrity through `file_digest`, `merkle_root_digest`, and `chain_head_digest`,
- and sealing receipts can commit to ordered segment sets.

But one expensive ambiguity remained:

**the archive never said exactly how those digests are computed, and the canonical examples still used placeholders for the event-journal chain itself.**

That omission is expensive because it quietly turns the event lane back into folklore:

- support bundles can point at `event.segment` digests without proving how those digests were derived,
- segment continuity can drift across implementations because `chain_head_digest` is described but not mechanically specified,
- `event.seal.receipt.segments_root_digest` can mean “some hash over some list” instead of a reproducible ordered commitment,
- and the archive stops being a good implementation target right where post-incident integrity matters most.

The design goal here is small and practical:
make the event lane mechanically checkable without inventing a new subsystem or a new product-profile key.

## Decision

1. Standardize `event.record.prev_digest` as:
   - `sha256( utf8( JCS(previous_event_record) ) )`
   - over the previous `event.record` object exactly as stored in the stream.

2. Standardize `event.segment.merkle_root_digest` as:
   - a sha256 Merkle root over the ordered per-record digests for the segment,
   - where each leaf digest is `sha256( utf8( JCS(event_record) ) )`,
   - and odd levels duplicate the final leaf.

3. Standardize `event.segment.chain_head_digest` as:
   - `sha256( utf8( JCS(chain_envelope) ) )`
   - where `chain_envelope` contains `stream_id`, `segment_id`, `file_digest`, `count`, `first_at`, `last_at`, and any present `merkle_root_digest` / `prev_chain_head_digest`.

4. Standardize `event.seal.receipt.segments_root_digest` as:
   - `sha256( utf8( JCS({"stream_id": receipt.stream_id, "segments": [{"segment_id","file_digest"}, ...]}) ) )`
   - using the exact ordered segment list committed by the receipt.

5. Keep the scope narrow.
   - This ADR does **not** introduce a new event-transport protocol,
   - does **not** force sealing on every profile,
   - and does **not** define a distributed transparency log for local events.

6. Make the canonical examples exact.
   - `spec/examples/event.record.json`, `spec/examples/event.segment.json`, and `spec/examples/event.seal.receipt.json` now bind real digests.
   - `spec/examples/event.segment.host-host-4f2a.seg-000001.jsonl` is the companion segment blob used for the example file/segment/seal proofs.

## Consequences

- The event journal lane becomes a better implementation target because the canonical examples now demonstrate a real proof chain instead of placeholder folklore.
- Offline support/export tooling can verify the same event-segment and seal commitments the archive describes.
- Future drift in event-chain computation becomes CI-detectable instead of surfacing only during incident response.

## What this does not decide

This ADR does **not** decide:

- the final on-disk journal format,
- whether segments are compressed in every deployment,
- the final key-management backend for sealing,
- or whether every product profile enables sealing by default.

It only closes the exact digest boundary for the event journal lane.
