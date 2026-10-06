# ADR-0351: Removable-media local fallback post-detach query projection is typed and negative-tested

- Status: accepted
- Date: 2026-05-21
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0350-removable-media-local-fallback-post-detach-recovery-evidence-is-typed-and-negative-tested.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`, `spec/removable.media.local.post_detach.query.projection.schema.json`

## Context

ADR-0350 made recovery evidence typed, but successful cleanup still leaves a second authority question: who may query the resulting receipt state, and what exactly may the index reveal? A rich receipt surface can accidentally become a raw media-path, device-hint, host-identity, filename, or full-text index. That would turn the evidence system into a new ambient observation channel immediately after the worker itself was carefully stripped of ambient authority.

## Decision

Add `spec/removable.media.local.post_detach.query.projection.schema.json` with kind `removable.media.local.post_detach.query.projection`, the canonical example `spec/examples/removable.media.local.post_detach.query.projection.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-query-projection/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-query-projection-positive-and-negative-fixture-guarded`, `sha256:5656565656565656565656565656565656565656565656565656565656565656`, and `known-bad-query-projection-shapes-must-fail-validation` in the recovery evidence, post-detach contract backend evidence, canonical content import plan/receipt, and preopen map. Querying the derivative receipt surface is admitted only as a lease-bound, redacted, derived projection after recovery evidence validates. The authoritative receipts remain the authority; the query index is a digest-bound derived snapshot.

The first projection intentionally excludes raw media paths, observed attach hints, device labels/serials, host paths, host user/home identity, untrusted filenames, and body/full-text content. It admits only a minimal allowlisted field set: receipt digest, contract digest, recovery evidence digest, preserved capture digest, derivative output digest, creation time, status, redaction profile, and lease digest.

## Consequences

- Receipt queryability becomes a typed evidence boundary rather than an ambient metadata convenience.
- The query/index layer cannot silently reintroduce media/device/user/path authority after r504-r506 removed it from the worker lane.
- Live subscriptions, cross-lane joins, aggregate counts, unbounded retention, full-text indexing, and filename indexing stay out of the first ordinary lane.
- Negative fixtures make leakage explicit: query without lease, raw media path leakage, observed-hint indexing, full-text indexing, host-identity leakage, open-ended live subscription, unbounded retention, cross-lane ambient joins, and filename indexing all fail validation.

## Alternatives considered

- **Let receipt stores be globally searchable by default.** Rejected because queryability is observation authority and can leak what the worker was forbidden to observe or persist.
- **Trust redaction prose in support/export tools.** Rejected because the projection surface must be schema-backed and red-tested before humans depend on it.
- **Store only opaque receipt digests and require manual inspection.** Rejected because DeriveBSD still needs useful incident and support workflows; the correct compromise is a minimal derived projection with lease-bound access.

## Follow-up

- Teach the first launcher/indexer prototype to emit `removable.media.local.post_detach.query.projection` after recovery evidence validates.
- Add a future generic `evidence.query.projection` only after this narrow removable-media lane proves stable.
- Consider thresholded aggregate-count projections for incident bundles without turning them into cross-origin enumeration surfaces.

## Links

- boundary doc: `docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.query.projection.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.query.projection.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-query-projection/`
- metadata background: `docs/293-attribute-indexed-metadata-and-live-queries.md`
