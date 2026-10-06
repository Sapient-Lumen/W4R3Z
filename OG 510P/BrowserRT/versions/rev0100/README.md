# rev0100: preserve valid blocks during failed-put rollback

Archive label: **rev0100**. Packaged version: **0.0.100**. Filename date: **2026-06-10**. Preserved extracted files: **1,039**.

[Original ZIP](BrowserRT-rev0100-2026.06.10.02.05-opfs-block-store-rollback-valid-block-preserve-current-proof.zip) · [Original README](contents/README.md) · [Start here](contents/START_HERE.md) · [Revision receipt](contents/REVISION-RECEIPT.json) · [Project index](../../README.md)

## Why this snapshot matters

The [rollback implementation](contents/src/opfs-block-store.mjs) inspects an owned final block before deleting it after a failed put. If its content matches the content-addressed path, the failure path preserves it and records `valid-final-block-preserved`; invalid, missing, or unreadable cases retain best-effort cleanup.

The [slice description](contents/docs/40-validation/opfs-block-store-rollback-valid-block-preserve-slice.md) makes the important limitation explicit: a failed call may leave a valid block, and that side effect is not an acknowledged application-level commit. This is not a transaction-system claim.

## Useful reading

- [Fake-OPFS probe source](contents/tools/opfs_block_store_rollback_valid_block_preserve_probe.mjs) and [carried result](contents/artifacts/validation/REV0100-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-PROBE.json)
- [Managed-browser slice](contents/docs/40-validation/browser-opfs-block-store-rollback-valid-block-preserve-slice.md) and [carried Chromium result](contents/artifacts/validation/REV0100-BROWSER-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-PROBE.json)

Both supplied result files record `passed`. The release-tier record covers late trace failure, late abort, and invalid-write cleanup; the Chromium record covers its named browser case. Neither was rerun for this showcase. The original README keeps release checks browser-light and withholds cross-browser behavior, quota/eviction survival, fsync or power-loss durability, fairness, multi-tab atomicity, and production readiness.

Editorial caution: some package/receipt metadata still describes rev0099's write-budget duplicate bypass. The current README, `summary_highlight`, code, and named rev0100 probes identify the rollback-preservation focus. Older README sections are explicitly carried history.

The ZIP is preserved separately from its extracted contents. Historical instructions remain inert archival material. No license is added by this guide.
