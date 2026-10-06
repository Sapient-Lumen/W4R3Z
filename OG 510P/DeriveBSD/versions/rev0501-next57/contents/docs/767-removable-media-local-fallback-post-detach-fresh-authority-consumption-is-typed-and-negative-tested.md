# Removable-media local fallback post-detach fresh authority consumption is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 closed the worker contract, r505 closed launch evidence, r506 closed recovery evidence, r507 closed query projection, r508 closed redacted export bundles, r509 closed revocation tombstones, r510 closed denial receipts, and r511 closed the legitimate fresh-authority reissue path. r512 closes the next edge: a fresh-authority receipt is not itself a reusable renewal token. It must be consumed once, with a typed receipt, before any successor query/export/rehydration/remote-locator/managed-copy authority is usable.

See also:
- ADR: `adrs/ADR-0356-removable-media-local-fallback-post-detach-fresh-authority-consumption-is-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.fresh.authority.consumption.receipt.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-fresh-authority-consumption-receipt/`
- fresh authority: `docs/766-removable-media-local-fallback-post-detach-fresh-authority-reissue-is-typed-and-negative-tested.md`
- denial receipt: `docs/765-removable-media-local-fallback-post-detach-denial-receipts-are-typed-and-negative-tested.md`
- query projection: `docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-fresh-authority-consumption-positive-and-negative-fixture-guarded`
- `sha256:a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4`
- `known-bad-post-detach-fresh-authority-consumption-shapes-must-fail-validation`

A `removable.media.local.post_detach.fresh.authority.consumption.receipt` is required before a fresh-authority receipt mints usable successor authority. The receipt records `fresh-authority-consumed-once-successor-artifacts-bound`, consumes the fresh lease exactly once, binds exact successor artifact digests, preserves the old tombstone/denial evidence, and rejects raw handle/locator/filename/host identity leakage.

## Evidence object shape

`spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.schema.json` requires these closed-world sections:

- `contract_binding`: joins the consumption receipt to the r504 contract, r505 launch evidence, r506 recovery evidence, r507 query projection, r508 export bundle, r509 tombstone, r510 denial receipt, r511 fresh-authority receipt, and canonical import receipt;
- `consumed_authority`: records the fresh-authority receipt digest, fresh lease digest, single-consumption mode, consumed time, actor/approval digests, and no stale-handle/raw-handle reuse;
- `minted_successors`: records exact successor query/export/rehydration/managed-copy/remote-locator digests and rejects pattern subjects, broadening, raw locators, filenames, and host identity;
- `consumption_decision`: records `fresh-authority-consumed-once-successor-artifacts-bound`, no double-spend, no tombstone/denial mutation, successor binding, no secret material, and no offline-erasure claim;
- `evidence_state`: records monotonic sequence, append-only log digest, consumed-marker digest, successor-index update, replay protection, redaction preservation, and absence of raw receipt payload/body/recipient/host identity;
- `observability`: exposes only redacted digest/purpose/consumption summaries;
- `failure_policy`: fails closed on missing fresh authority, lease reuse/double-spend, missing consumed marker, scope broadening, pattern successors, raw locator/handle leakage, tombstone/denial mutation, missing successor index update, secret material, or offline-erasure overclaim.

## Red corpus

The fresh-authority consumption red corpus starts under `spec/examples/invalid/removable-media/post-detach-fresh-authority-consumption-receipt/` with:

- `missing-fresh-authority-receipt.json`
- `lease-reuse-allowed.json`
- `double-spend-allowed.json`
- `broad-successor-scope.json`
- `pattern-successor-subject.json`
- `raw-locator-included.json`
- `tombstone-mutated.json`
- `missing-consumed-marker.json`
- `missing-successor-index-update.json`
- `secret-material-present.json`
- `offline-erasure-claimed.json`

Each fixture is intentionally close to the canonical object and must fail validation. This keeps a fresh-authority receipt from becoming an untracked retry/renewal handle.

## What this changes in implementation terms

The first launcher/indexer prototype now has nine separate artifacts in this lane:

1. the r504 contract says which authority is allowed;
2. the r505 launch evidence says what the FreeBSD backend observed at launch;
3. the r506 recovery evidence says what survived and whether derivative receipt visibility is allowed;
4. the r507 query projection says what may be searched about the receipt;
5. the r508 export bundle says what may leave the host or enter support/incident handoff;
6. the r509 revocation tombstone says when old query/export/rehydration handles stop working;
7. the r510 denial receipt proves stale use was denied after the tombstone;
8. the r511 fresh-authority receipt proves later successor authority came from a fresh lease and policy decision;
9. the r512 consumption receipt proves that fresh authority was applied once to exact successor artifacts.

The behavioral change is "reissue authority is consumed," not "reissue authority remains available until someone notices expiry." The consumed marker is audit evidence and replay protection.

## Notes for backend implementers

The query broker, export broker, rehydration broker, remote-object adapter, and managed-copy adapter should treat a fresh-authority receipt like a one-shot plan. Before any successor handle is live, they must write the consumption receipt, mark the fresh lease consumed, update the redacted successor index, and reject later attempts to spend the same fresh-authority digest again. The receipt may point to old tombstone, denial, and fresh-authority digests, but it must not include raw handles, raw paths, original filenames, recipient text, host identity, full receipt payloads, body text, or secret material.

A support operator should be able to answer: "Was fresh authority issued?" and "Was it consumed once to mint these successor digests?" without seeing the raw removable-media locator.

## r513 successor-index cutover

r513 adds `typed-post-detach-successor-index-cutover-positive-and-negative-fixture-guarded`, `sha256:b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3`, and `known-bad-post-detach-successor-index-cutover-shapes-must-fail-validation` with `removable.media.local.post_detach.successor.index.cutover.receipt` so the `successor_index_update_digest` recorded by this receipt is no longer an untyped promise. A successor query/export/rehydration/remote-locator/managed-copy row is usable only after `successor-index-cutover-old-handles-terminal-successors-exact` proves the old tombstoned handles are terminal, the exact r512 successors are live, and no dual-active, forked, orphaned, rollbackable, raw-locator, filename, host-identity, full-text, or secret-bearing index state was admitted.

## Hygiene

`tools/check_removable_media_local_post_detach_fresh_authority_consumption_receipt.py` validates the positive consumption fixture, proves the red corpus fails, and keeps `typed-post-detach-fresh-authority-consumption-positive-and-negative-fixture-guarded`, `sha256:a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4`, and `known-bad-post-detach-fresh-authority-consumption-shapes-must-fail-validation` wired through the fresh-authority receipt, denial receipt, revocation tombstone, export bundle, query projection, recovery evidence, contract, content import plan/receipt, and preopen map.

Last updated: 2026-05-23r513
