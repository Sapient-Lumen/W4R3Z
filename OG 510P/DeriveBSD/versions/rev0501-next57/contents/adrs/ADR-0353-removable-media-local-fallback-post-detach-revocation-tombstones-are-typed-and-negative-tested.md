# ADR-0353: Removable-media local fallback post-detach revocation tombstones are typed and negative-tested

- Status: accepted
- Date: 2026-05-21
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0352-removable-media-local-fallback-post-detach-export-bundles-are-redacted-and-negative-tested.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`, `spec/removable.media.local.post_detach.export.bundle.schema.json`

## Context

ADR-0352 made support and incident bundles a redacted export boundary. That still leaves a lifetime problem: a query handle, export approval, recipient-bound bundle, or digest-rehydration affordance can be copied into another workflow and used later unless revocation has a typed, queryable denial artifact. Informal retention limits are not enough, and a cleanup job that claims to erase already-exported offline copies would overstate what DeriveBSD can prove.

## Decision

Add `spec/removable.media.local.post_detach.revocation.tombstone.schema.json` with kind `removable.media.local.post_detach.revocation.tombstone`, the canonical example `spec/examples/removable.media.local.post_detach.revocation.tombstone.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-revocation-tombstone/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-revocation-tombstone-positive-and-negative-fixture-guarded`, `sha256:6666666666666666666666666666666666666666666666666666666666666666`, and `known-bad-post-detach-revocation-tombstone-shapes-must-fail-validation` in the r508 export bundle, r507 query projection, r506 recovery evidence, r504 post-detach contract backend evidence, canonical content import plan/receipt, and post-detach preopen map.

A revocation tombstone denies future query, export, and digest-rehydration authority for exact digest-bound subjects after explicit revocation or expiry. It does not claim that offline copies already outside host control have been erased. Remote-object or managed local copies must record delete/revoke receipts when present; otherwise the tombstone records future-authority denial and historical-existence limits.

## Consequences

- Stale query and export handles fail closed after tombstone visibility.
- Digest rehydration requires fresh authority after tombstoning instead of silently joining old bundle digests back to authoritative receipts.
- Tombstones become redacted evidence objects: reason and digest subjects are visible; raw paths, locators, host identity, recipient identity text, and secrets are not.
- The lane stops promising impossible erasure of offline copies, while still preventing live locators, managed copies, and rehydration brokers from acting as stale authority.
- Negative fixtures make common revocation mistakes executable: stale query/export acceptance, stale rehydration, prefix revocation, raw locator leakage, false offline-erasure claims, missing deletion receipts, unbounded tombstone retention, secret material, and successor authority without a fresh lease all fail validation.

## Alternatives considered

- **Let export-bundle retention policy do the work.** Rejected because retention describes desired lifetime; it does not provide a denial artifact that query, export, and rehydration brokers can check.
- **Claim exported bundles are erased on revocation.** Rejected because offline copies outside host control may still exist. The tombstone must be honest about what it proves.
- **Use pattern or prefix revocation.** Rejected for the first lane because broad matching can accidentally deny unrelated receipts or leak structure through denial behavior.

## Follow-up

- Teach the first launcher/indexer prototype to consult `removable.media.local.post_detach.revocation.tombstone` before query projection, export bundle creation, and digest rehydration.
- Define a future generic evidence tombstone only after this lane proves the exact-digest subject model.
- Add UX copy that distinguishes “future authority revoked” from “external copy erased.”

## Links

- boundary doc: `docs/764-removable-media-local-fallback-post-detach-revocation-tombstones-are-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.revocation.tombstone.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.revocation.tombstone.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-revocation-tombstone/`
- export bundle: `docs/763-removable-media-local-fallback-post-detach-export-bundles-are-redacted-and-negative-tested.md`
