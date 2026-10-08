# Rev0984 changelog

## Runtime and editor

- Added logical UTF-8 retained-text accounting to linear undo/redo rows, with cached per-stack/per-buffer totals rather than history rescans.
- Added global/local `undobytes` with a 32 MiB default and `0` for unlimited history text.
- Added deque-backed complete-oldest-row budget trimming that preserves compound transaction boundaries and the newest recovery row without shifting surviving history.
- Added visible trim and soft-overage messages plus the `undostatus` command; compatible consecutive budget feedback keeps accumulated trim totals and only the newest overage rows in an authority-safe bounded tail.
- Protected `undobytes` from lower-authority script writes while allowing read-only inspection.
- Dropped callback-dead equal splice strings from sidecar-only compact rows.
- Compacted aggregate undo snapshots to full state for changed buffer objects and membership-only rows for untouched buffers.
- Reused unchanged immutable text in successful transaction after-snapshots by buffer version.
- Removed an eager saved-signature fallback that joined and hashed every open document even when `_saved_sig` existed.

## Evidence

- Added `tools/measure_history_retention.py` and `.artifacts/rev0984-history-retention.json`.
- Added accounting-cache/no-rescan, seeded cache-oracle, snapshot-rebuild, branch-release, whole-row/multi-owner trimming, authority-safe bounded trim/overage feedback, script-policy, status, snapshot-reuse, transaction-compaction, exact undo/redo, and witness regressions.
- Added the deep resource/product audit in `docs/941-retained-history-budget-transaction-snapshot-compaction.md`.

## Scope

This revision provides a soft logical-text budget, not a hard process-memory bound. The newest row may exceed its limit. Metadata-only rows, callback overhead, native/RSS allocation, initial all-buffer rollback capture, multi-cursor/query-replace/line-plan snapshots, typing coalescing, persistent history, undo trees, and text-engine replacement remain outside the claim.

## Release handoff

- Rolled the compact generated-context window from twelve to eleven recent revision entries after core-plus-recent evidence reached 66 paths against the declared 64-path ceiling. Current revision and core evidence remain complete; the oldest catalog-backed entry ages out deliberately instead of current paths being silently omitted.
- Replaced the fixed four-name `.artifacts` packaging allowlist for revision receipts with a canonical `rev####-lowercase-hyphen.json` convention, strict object-JSON validation, and a 1 MiB per-receipt ceiling. The rev0984 retention witness is now present in the archive it documents.
