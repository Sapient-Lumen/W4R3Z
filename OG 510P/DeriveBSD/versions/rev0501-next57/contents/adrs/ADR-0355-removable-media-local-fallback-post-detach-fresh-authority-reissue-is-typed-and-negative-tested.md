# ADR-0355: Removable-media local fallback post-detach fresh authority reissue is typed and negative-tested

- Status: accepted
- Date: 2026-05-22
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0354-removable-media-local-fallback-post-detach-denial-receipts-are-typed-and-negative-tested.md`, `adrs/ADR-0353-removable-media-local-fallback-post-detach-revocation-tombstones-are-typed-and-negative-tested.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Context

ADR-0354 made stale query, export, rehydration, remote-locator, and managed-copy attempts auditable denial events after a revocation tombstone. That still leaves the legitimate successor path easy to blur: operators and users may need access again, but the old handle must not become a renewal token, the tombstone must not be mutated away, and support/debug paths must not smuggle raw locators or filenames into a "try again" bundle.

## Decision

Add `spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json` with kind `removable.media.local.post_detach.fresh.authority.receipt`, the canonical example `spec/examples/removable.media.local.post_detach.fresh.authority.receipt.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-fresh-authority-receipt/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-fresh-authority-receipt-positive-and-negative-fixture-guarded`, `sha256:7171717171717171717171717171717171717171717171717171717171717171`, and `known-bad-post-detach-fresh-authority-receipt-shapes-must-fail-validation` in the r510 denial receipt, r509 revocation tombstone, r508 export bundle, r507 query projection, r506 recovery evidence, r504 post-detach contract backend evidence, canonical content import plan/receipt, and post-detach preopen map.

A fresh-authority receipt is the only normal successor after tombstone-caused denial. It binds the visible tombstone and denial receipt, records fresh user or admin authority, mints new exact digest subjects and a new lease digest, preserves the old tombstone, and says explicitly that unmanaged offline copies are not erased.

## Consequences

- Stale handles are never renewal handles.
- Legitimate reissue has an auditable path without weakening r509/r510 denial semantics.
- Query/export/rehydration brokers can distinguish denial evidence from reauthorization evidence.
- Successor authority must be same-or-narrower than the original projection and exact-digest-bound.
- Negative fixtures make common renewal mistakes executable: missing denial causality, stale-handle reuse, tombstone mutation, broad successor scope, pattern subjects, raw locator leakage, missing fresh lease, no user presence, secret material, and offline-erasure overclaim all fail validation.

## Alternatives considered

- **Reuse the stale handle after a prompt.** Rejected because the stale handle would become a standing renewal capability.
- **Delete or mutate the tombstone when access is restored.** Rejected because the tombstone is audit evidence; fresh authority should supersede by digest join, not erase history.
- **Let support bundles carry a manual override.** Rejected because that bypasses the query/export redaction chain and reintroduces raw locator pressure.

## Follow-up

- Teach query/export/rehydration brokers to emit `removable.media.local.post_detach.fresh.authority.receipt` when a user/admin deliberately reissues access after a tombstone-caused denial.
- Add UX copy that says "new access was issued" rather than "the old access was restored."
- Consider a later cross-lane lease-renewal pattern once more domains need the same tombstone/denial/fresh-authority triad.
