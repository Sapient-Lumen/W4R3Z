# Removable-media local fallback post-detach terminal closure successor cutover and successor-index cutover schema split

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, supply-chain
**Patterns:** Broker→Lease→Receipt, Capsule, Registry→Diff→Gate

## Problem

r532 made successor authority after terminal closure safe to issue, but not yet safe to activate. The lane needed a receipt that proves the successor authority only becomes usable after the older successor-index cutover/checkpoint/reader-admission fences are observed.

The cube schema audit also kept `spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json` as the highest-priority const-heavy post-detach runtime surface.

## Change

r533 adds `removable.media.local.post_detach.terminal.closure.successor.cutover.receipt` with `post-detach-terminal-closure-successor-cutover-positive-and-negative-fixture-guarded`. The receipt binds the r532 successor-authority receipt, r513 successor-index cutover, r514 successor-index checkpoint, r515 reader admission, and r521 support projection by computed digest.

The receipt proves:

- successor authority is bound and still came from fresh authority only;
- successor-index cutover observed before activation;
- old handles are terminal and no dual-active index window is accepted;
- checkpoint observed before broker use;
- reader admission is bound before use;
- the activation ledger advances by compare-and-swap;
- terminal closure remains terminal;
- support visibility remains `support-safe-digest-only` and offline erasure is not overclaimed.

r533 also preserves `typed-post-detach-successor-index-cutover-positive-and-negative-fixture-guarded` while adding `post-detach-successor-index-cutover-generic-runtime-schema-plus-exact-fixture-split`: `spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json` is now the runtime contract, while `spec/removable.media.local.post_detach.successor.index.cutover.receipt.fixture.schema.json` preserves the exact r513 example.

## Negative corpus

The red corpus rejects missing or stale successor-authority binding, unobserved cutover, unobserved checkpoint, dual-live old index state, broadened successor authority, stale or missing reader admission, raw support visibility, non-advancing activation roots, broker use before checkpoint/admission, and terminal-closure reopening.

## Validation

Run:

```bash
python3 tools/check_removable_media_local_post_detach_terminal_closure_successor_cutover_receipt.py
python3 tools/check_removable_media_local_post_detach_successor_index_cutover_receipt.py
python3 tools/check_cube_schema_refactor_backlog.py
```

Last updated: 2026-05-30r533
