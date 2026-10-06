# Removable-media local fallback post-detach terminal closure access and fresh authority schema split

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, supply-chain
**Patterns:** Broker→Lease→Receipt, Capsule, Registry→Diff→Gate

## Problem

r530 made terminal closure explicit, but a later use of old managed authority still needed a per-attempt artifact. The capsule says future access is denied; it does not itself prove that a later query, export, rehydration, reader observation, managed-copy, or support-debug attempt was actually gated.

The cube schema audit also kept `spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json` as the next highest-priority const-heavy post-detach runtime surface.

## Change

r531 adds `removable.media.local.post_detach.terminal.closure.access.receipt` with `post-detach-terminal-closure-access-positive-and-negative-fixture-guarded`. The receipt binds the terminal closure capsule, export deletion receipt, denial-selection receipt, denial reason registry, rate-limit debit ledger receipt, and support projection by computed digest. It then records a post-closure access decision:

- the terminal closure capsule was checked before the decision;
- the selected gate reason is `terminal-closure-managed-authority-closed`;
- old managed authority is denied for query, export, rehydrate, observe, managed-copy, and support-debug;
- successor authority requires new authority rather than resurrection of the old handle;
- export and managed-copy require new approval;
- support projection stays `support-safe-digest-only`;
- the access gate advances a CAS-rooted access ledger and debits rate limits once.

r531 also adds `post-detach-fresh-authority-generic-runtime-schema-plus-exact-fixture-split`: `spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json` is now the runtime contract, while `spec/removable.media.local.post_detach.fresh.authority.receipt.fixture.schema.json` preserves the exact r511 example.

## Negative corpus

The red corpus rejects missing or stale terminal closure bindings, old authority acceptance, query allowance after closure, export without new approval, rehydration live locators, observation that mints a successor from old authority, raw support visibility, missing rate-limit debit, and non-advancing access ledger roots.

## Validation

Run:

```bash
python3 tools/check_removable_media_local_post_detach_terminal_closure_access_receipt.py
python3 tools/check_removable_media_local_post_detach_fresh_authority_receipt.py
python3 tools/check_cube_schema_refactor_backlog.py
```

Last updated: 2026-05-30r531
