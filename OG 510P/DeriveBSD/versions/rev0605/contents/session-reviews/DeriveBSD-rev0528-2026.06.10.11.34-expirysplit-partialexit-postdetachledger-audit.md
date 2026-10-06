# DeriveBSD rev0528 session audit — expiry split and partial-exit ledger hardening

## Focus

This revision kept the pass implementation-heavy: close the next p0 schema-cube split, then correct a practical completion-risk issue in the resumable hygiene runner. The target was `removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt` because it sits in the reader-use retention tail and feeds enforcement receipts.

## Substantive changes

- Split `spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.schema.json` into a generic runtime schema plus `spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.fixture.schema.json` for exact historical literals.
- Updated `tools/check_removable_media_local_post_detach_reader_use_ledger_retention_expiry_receipt.py` so the canonical example validates against both the runtime contract and the exact fixture schema.
- Updated expiry/enforcement coupling so exact historical digests stay on fixture schemas while runtime schemas keep generic digest/path/id/timestamp shape.
- Corrected `tools/hygiene.py` ledger-mode shell semantics: a completed all-passing ledger returns `0`, a checker failure or timeout returns `1`, and an otherwise clean incomplete budgeted chunk returns `2`.
- Extended `tools/check_cube_hygiene_run_ledger.py` regression coverage to lock the partial-exit behavior.
- Refreshed generated/current cube surfaces for r560.

## Why this matters

The prior chunking work made long post-detach/release-critical profiles resumable, but shell wrappers could still mistake a clean partial chunk for a completed profile if they only looked at the process exit code. That is exactly the kind of cloudtainer failure mode that creates false confidence. Rev0528 makes partial evidence explicit at both the ledger level and the shell boundary.

The schema split removes another p0 exact-fixture surface from the runtime path. Runtime consumers now validate the retention-expiry receipt shape without freezing canonical historical digests in the production contract; the fixture schema still preserves exact regression evidence.

## Validation evidence

- `release-critical`: 35/35 passed after an input-fingerprinted resume.
- `post-detach`: 39/39 passed via small explicit chunks; partial chunks returned exit code 2 until the final complete pass.
- `schema-cube-audit`: 3/3 passed.
- `generated-surface`: 2/2 passed.
- Direct target checker passed.
- `tools/check_cube_hygiene_run_ledger.py` passed.
- `tools/lint_spec_schemas.py` passed.
- `tools/validate_spec_examples.py` passed for 467 examples.

## Current cube audit movement

- Schemas: 454.
- Examples: 467.
- Runtime-contract-shaped schemas: 39.
- Exact fixture schemas: 16.
- Backlog items: 25 total, 16 completed, 9 open.
- Audit next target: `spec/removable.media.local.post_detach.launch.evidence.schema.json`.

## Next recommended cut

Split launch evidence next. It is the last audit-next p0 target and is riskier than the remaining backlog because it is close to the fd-bound worker launch proof surface. After that split, audit downstream launch/recovery/contract-closure checkers for hidden exact-digest coupling, the same pattern corrected across the reader-use retention tail.
