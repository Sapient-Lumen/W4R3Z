# Removable-media local fallback post-detach terminal closure successor authority and reader admission schema split

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, supply-chain
**Patterns:** Broker→Lease→Receipt, Capsule, Registry→Diff→Gate

## Problem

r531 made old managed authority fail closed after terminal closure, but it did not yet describe the safe positive path. A later broker still needed an artifact that proves new authority after closure came from a fresh-authority receipt, not from resurrection of the old handle or reopening of the terminal capsule.

The cube schema audit also kept `spec/removable.media.local.post_detach.reader.admission.receipt.schema.json` as the highest-priority const-heavy post-detach runtime surface.

## Change

r532 adds `removable.media.local.post_detach.terminal.closure.successor.authority.receipt` with `post-detach-terminal-closure-successor-authority-positive-and-negative-fixture-guarded`. The receipt binds the terminal closure capsule, the terminal-closure access receipt, the fresh-authority receipt, denial reason/selection artifacts, the rate-limit debit ledger receipt, the support projection, and reader admission by computed digest.

The receipt proves:

- old managed authority was denied before successor issuance;
- the prior denial was rate-limit accounted;
- the closure state seen by the new request was `managed-authority-terminally-closed`;
- the fresh-authority receipt, approval digest, policy digest, and new lease digest are bound exactly;
- the successor outcome is `successor-authority-issued-from-new-authority-only`;
- terminal closure is not reopened and expired roots are not resurrected;
- export requires new approval and reader use requires reader admission;
- support projection remains `support-safe-digest-only`.

r532 also preserves `typed-post-detach-reader-admission-positive-and-negative-fixture-guarded` while adding `post-detach-reader-admission-generic-runtime-schema-plus-exact-fixture-split`: `spec/removable.media.local.post_detach.reader.admission.receipt.schema.json` is now the runtime contract, while `spec/removable.media.local.post_detach.reader.admission.receipt.fixture.schema.json` preserves the exact r515 example.

## Negative corpus

The red corpus rejects missing or stale terminal-closure access binding, old authority presented as new authority, fresh-authority stale-handle reuse, expired-root resurrection, terminal-closure reopening, missing reader-admission requirement, old export approval carry-forward, raw support visibility, non-advancing successor ledger roots, and missing rate-limit proof for the prior denial.

## Validation

Run:

```bash
python3 tools/check_removable_media_local_post_detach_terminal_closure_successor_authority_receipt.py
python3 tools/check_removable_media_local_post_detach_reader_admission_receipt.py
python3 tools/check_cube_schema_refactor_backlog.py
```

Last updated: 2026-05-30r532
