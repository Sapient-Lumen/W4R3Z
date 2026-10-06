# Removable-media local fallback post-detach terminal closure and denial receipt schema split

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, supply-chain
**Patterns:** Broker→Lease→Receipt, Capsule, Registry→Diff→Gate

## Problem

r529 made export-bundle deletion terminal and ledgered, but a reviewer still had to stitch together export deletion, denial selection, support projection, transition witnesses, and scenario replay to know whether the whole post-detach lane was closed. The lane needed one capsule that says the managed authority graph has reached terminal closure.

The cube schema audit also kept `spec/removable.media.local.post_detach.denial.receipt.schema.json` as the next highest-priority const-heavy post-detach runtime surface.

## Change

r530 adds `removable.media.local.post_detach.terminal.closure.capsule` with `post-detach-terminal-closure-positive-and-negative-fixture-guarded`. The capsule binds:

- the r529 export-bundle deletion receipt by computed digest;
- the r528 export-bundle access receipt, r509 revocation tombstone, r510 denial receipt, r525 denial-selection receipt, r524 denial reason registry, r521 support projection, r523 transition witness, and r522 scenario replay by computed digest;
- terminal managed export posture and future access denial without new authority;
- no expired-root or old-handle resurrection;
- explicit non-claim of unmanaged offline-copy erasure;
- support-safe digest-only projection;
- CAS-rooted terminal closure ledger advancement after the deletion ledger.

r530 also adds `post-detach-denial-receipt-generic-runtime-schema-plus-exact-fixture-split`: `spec/removable.media.local.post_detach.denial.receipt.schema.json` is now the runtime contract, while `spec/removable.media.local.post_detach.denial.receipt.fixture.schema.json` preserves the exact r510 example.

## Negative corpus

The red corpus rejects missing or stale deletion bindings, stale denial-selection bindings, managed export left open, closure ledger roots that do not advance, raw support visibility, offline-erasure overclaims, expired-root resurrection, skipped transition-witness checks, and new export paths that do not require new approval.

## Validation

Run:

```bash
python3 tools/check_removable_media_local_post_detach_terminal_closure_capsule.py
python3 tools/check_removable_media_local_post_detach_denial_receipt.py
python3 tools/check_cube_schema_refactor_backlog.py
```

Last updated: 2026-05-30r530
