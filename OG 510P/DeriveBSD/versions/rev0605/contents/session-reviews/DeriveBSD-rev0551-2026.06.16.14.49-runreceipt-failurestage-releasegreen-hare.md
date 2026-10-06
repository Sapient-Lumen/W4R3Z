# DeriveBSD rev0551 session review — run receipts and failure-stage proof trail

This cut keeps pressure on the riskiest unfinished lane: real FreeBSD removable-media host proof. The previous revision made preserved handoffs resumable; this revision makes failed or resumed wrapper attempts observable by a machine-readable run receipt instead of relying on scrollback.

## Substantive changes

- Hardened `tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh` with `--run-receipt RUN_RECEIPT` and `DERIVEBSD_HOST_PROOF_RUN_RECEIPT`.
- The wrapper now writes `removable.media.local.freebsd.host.proof.collect_import.run.receipt` from its exit trap when requested.
- The run receipt records strict real-proof-only mode, current/failing stage, completed stages, handoff directory, import root, exit status, resume/replacement mode, and handoff-retention decision.
- Extended `tools/check_removable_media_local_fallback_freebsd_host_proof_collect_import.py` so release-critical executes a missing-handoff resume with `--run-receipt` and proves the receipt records failure at `verify_handoff` without rerunning collection.
- Kept the proof-tool digest set at exactly 12 rows; this is operator-safety hardening, not another proof registry family.
- Refreshed current front doors, generated docs/catalogs, host-smoke and proof-bundle examples, cube schema audit/backlog/checkset artifacts, and hygiene ledgers for `2026-06-16r581`.
- Refactored the current docs/index surface to keep the front-door budget green while still indexing both r581 and historical r580 cuts.

## Risk reduced

A scarce real-host attempt can now leave a durable failure trail even when it fails during verification, import, or audit. Operators get the failed stage and the exact handoff/import paths needed for recovery, while the wrapper still exposes no checker-simulation, refusal, or failed-proof flags.

## Validation

- `release-critical`: 45 / 45 passed.
- `schema-cube-audit`: 3 / 3 passed.
- Strict JSON duplicate-key scan: 1413 JSON files scanned.
- Python bytecode artifact check: clean.
- FreeBSD real-host proof theatre gate: no checked-in strict real-host proof claims; checker non-proof bundles validate only through explicit non-proof mode.

## Boundary

This revision still does not claim a non-simulated FreeBSD host receipt. The next true milestone remains running the strict collect/import wrapper on a supported real FreeBSD host, with `--run-receipt` set so any failure has a recovery trail.
