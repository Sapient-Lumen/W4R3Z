# Removable-media local fallback post-detach fresh authority reissue is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 closed the worker contract, r505 closed launch evidence, r506 closed recovery evidence, r507 closed query projection, r508 closed redacted export bundles, r509 closed revocation tombstones, and r510 closed denial receipts. r511 closes the legitimate successor path: after a tombstone-caused denial, renewed access is not a retry token, not a resurrected stale handle, and not a deletion of the tombstone. It is a fresh authority receipt with a new lease, new exact digest subjects, fresh user/admin authorization, and redacted evidence.

See also:
- ADR: `adrs/ADR-0355-removable-media-local-fallback-post-detach-fresh-authority-reissue-is-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.fresh.authority.receipt.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-fresh-authority-receipt/`
- denial receipt: `docs/765-removable-media-local-fallback-post-detach-denial-receipts-are-typed-and-negative-tested.md`
- revocation tombstone: `docs/764-removable-media-local-fallback-post-detach-revocation-tombstones-are-typed-and-negative-tested.md`
- query projection: `docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-fresh-authority-receipt-positive-and-negative-fixture-guarded`
- `sha256:7171717171717171717171717171717171717171717171717171717171717171`
- `known-bad-post-detach-fresh-authority-receipt-shapes-must-fail-validation`

A `removable.media.local.post_detach.fresh.authority.receipt` is required whenever the system creates successor query, export, rehydration, remote-locator, or managed-copy authority after a tombstone-caused denial. The successor must be same-or-narrower than the original projection, exact-digest-bound, and backed by a fresh lease plus a fresh policy decision. The old handle remains stale, and the tombstone remains audit evidence.

## Evidence object shape

`spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json` requires these closed-world sections:

- `contract_binding`: joins the fresh-authority receipt to the r504 contract, r505 launch evidence, r506 recovery evidence, r507 query projection, r508 export bundle, r509 tombstone, r510 denial receipt, and canonical import receipt;
- `actor_intent`: records fresh user/admin authority, purpose, approval receipt, and absence of raw handle values or ambient reauthentication;
- `successor_subjects`: records new exact digest subjects and rejects stale-handle reuse, pattern subjects, raw locators, filenames, and host identity;
- `authority_decision`: records `fresh-lease-issued-with-new-digest-subject`, no tombstone mutation, no offline-erasure claim, and same-or-narrower scope;
- `evidence_state`: records tombstone/denial observation, monotonic sequence, new lease receipt, policy decision receipt, index update receipt, redaction preservation, and secret absence;
- `observability`: exposes only digest/purpose/fresh-lease summaries to query/support surfaces;
- `failure_policy`: fails closed on stale-handle reuse, missing denial/tombstone causality, broad successor scope, missing fresh lease, missing user/policy authority, tombstone mutation, raw locator leakage, or secret material.

## Red corpus

The fresh-authority red corpus starts under `spec/examples/invalid/removable-media/post-detach-fresh-authority-receipt/` with:

- `missing-denial-receipt-causality.json`
- `stale-handle-reused.json`
- `old-tombstone-mutated.json`
- `broad-successor-scope.json`
- `pattern-successor-subject.json`
- `raw-locator-included.json`
- `no-fresh-lease.json`
- `no-user-presence.json`
- `secret-material-present.json`
- `offline-erasure-claimed.json`

Each fixture is intentionally close to the canonical object and must fail validation. This keeps renewal from becoming a hidden bypass around the tombstone/denial chain.

## What this changes in implementation terms

The first launcher/indexer prototype now has eight separate artifacts in this lane:

1. the r504 contract says which authority is allowed;
2. the r505 launch evidence says what the FreeBSD backend observed at launch;
3. the r506 recovery evidence says what survived and whether derivative receipt visibility is allowed;
4. the r507 query projection says what may be searched about the receipt;
5. the r508 export bundle says what may leave the host or enter support/incident handoff;
6. the r509 revocation tombstone says when old query/export/rehydration handles stop working;
7. the r510 denial receipt proves stale use was denied after the tombstone;
8. the r511 fresh-authority receipt proves any later successor authority came from a fresh lease and new policy decision, not from replaying the stale handle.

The important behavioral change is "reissue by fresh authority," not "undo revocation." A tombstone remains true after successor access is granted; successor authority is a new digest-joined object.

## Notes for backend implementers

The query broker, export broker, rehydration broker, remote-object adapter, and managed-copy adapter must not turn denial UX into a renewal API. A fresh-authority receipt should be emitted only after a fresh local user-presence or admin breakglass receipt and a new policy decision. It may point to old tombstone and denial digests, but it must not include raw handles, raw paths, original filenames, recipient text, host identity, receipt payloads, or secret material.

A support operator should be able to answer: "Was this old authority denied?" and "Was new authority deliberately issued later?" without ever seeing the raw removable-media locator.

## Hygiene

`tools/check_removable_media_local_post_detach_fresh_authority_receipt.py` validates the positive fresh-authority fixture, proves the red corpus fails, and keeps `typed-post-detach-fresh-authority-receipt-positive-and-negative-fixture-guarded`, `sha256:7171717171717171717171717171717171717171717171717171717171717171`, and `known-bad-post-detach-fresh-authority-receipt-shapes-must-fail-validation` wired through the denial receipt, revocation tombstone, export bundle, query projection, recovery evidence, contract, content import plan/receipt, and preopen map.

Last updated: 2026-05-22r512

## r512 consumption follow-up

r512 adds `typed-post-detach-fresh-authority-consumption-positive-and-negative-fixture-guarded` and `sha256:a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4` as the one-shot apply receipt for this fresh-authority object. A fresh-authority receipt can authorize successor issuance, but it is not usable as a recurring retry token; brokers must emit the r512 consumption receipt before successor handles become live.
