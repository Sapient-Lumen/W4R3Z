# ADR-0358: Removable-media local fallback post-detach successor index checkpoint is typed and negative-tested

- Status: accepted
- Date: 2026-05-23
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0357-removable-media-local-fallback-post-detach-successor-index-cutover-is-typed-and-negative-tested.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`, `docs/768-removable-media-local-fallback-post-detach-successor-index-cutover-is-typed-and-negative-tested.md`

## Context

ADR-0357 made successor-index cutover a typed receipt, but a later broker can still be confused if it reads an older index root, a restored backup, or a half-replayed log snapshot. The cutover receipt says the transition happened; it does not, by itself, define the minimum index checkpoint that query, export, rehydration, remote-locator, and managed-copy readers must accept before treating successor authority as live.

## Decision

Add `spec/removable.media.local.post_detach.successor.index.checkpoint.receipt.schema.json` with kind `removable.media.local.post_detach.successor.index.checkpoint.receipt`, the canonical example `spec/examples/removable.media.local.post_detach.successor.index.checkpoint.receipt.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-successor-index-checkpoint-receipt/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-successor-index-checkpoint-positive-and-negative-fixture-guarded`, `sha256:c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8`, and `known-bad-post-detach-successor-index-checkpoint-shapes-must-fail-validation` after the r513 cutover receipt. The checkpoint receipt anchors the cutover marker, successor index snapshot, tombstone root, denial-root, and successor-root digests to a monotonic append-only sequence. Brokers must reject any index root below the checkpoint sequence, any restored old-handle root, any dual-active snapshot, and any checkpoint that leaks raw locator, filename, host, full-text, body, recipient, receipt payload, or secret material.

## Consequences

- Cutover cannot be silently undone by stale index roots or backup restore.
- Query/export/rehydration brokers now have a typed reader fence: sequence 44 is the first acceptable post-cutover root for this lane.
- The checkpoint is an observation artifact, not new content authority: it contains digest roots and purpose summaries only.
- Negative fixtures make common mistakes executable: missing cutover receipt, non-monotonic sequence, stale root acceptance, old-handle restoration, dual-active snapshots, unanchored or mutable checkpoints, missing reader fences, raw locator/filename leaks, full-text indexing, secret material, and offline-erasure overclaim.

## Status

Accepted for the next implementation-shaped cut. Multi-writer checkpoint quorum, cross-host witness policy, and long-term compaction can be specified later, but they must preserve the digest-only/redacted reader-fence model.
