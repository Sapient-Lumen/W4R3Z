# rev0125: guarded staged recovery

Archive label and packaged runtime: **rev0125 / 0.0.125**. Filename date: **2026-06-18**. Preserved extracted files: **1,205**.

[Original ZIP](BrowserRT-rev0125-2026.06.18.17.53-opfs-block-store-raw-composite-abort-signal-current-proof-guarded-staged-recovery.zip) · [Original README](contents/README.md) · [Start here](contents/START_HERE.md) · [Revision receipt](contents/REVISION-RECEIPT.json) · [Project index](../../README.md)

## Why this snapshot matters

The snapshot retains OPFS Raw Composite AbortSignal as its named current proof while adding staged-recovery coordination. The [guard implementation](contents/src/opfs-web-lock-guarded-block-store.mjs) routes `recoverStagedWrites()` through the same exclusive-lock path used for guarded writes.

The original README and [probe source](contents/tools/opfs_block_store_guarded_staged_recovery_probe.mjs) contrast an unguarded cleanup race with recovery that waits behind an active guarded write. The boundary matters: participating providers must use the same Web Lock name/prefix. Direct raw providers remain uncoordinated.

## Useful reading

- [Raw OPFS provider](contents/src/opfs-block-store.mjs)
- [Guarded staged-recovery audit source](contents/tools/opfs_block_store_guarded_staged_recovery_contract_audit.mjs)
- [Carried guarded staged-recovery result](contents/artifacts/validation/REV0125-OPFS-BLOCK-STORE-GUARDED-STAGED-RECOVERY-PROBE.json)
- [Current composite-AbortSignal slice](contents/docs/40-validation/opfs-block-store-raw-composite-abort-signal-slice.md)

The carried recovery result records `status: passed` and `compactedEvidence: true`, with empty `proof` and `stats` objects. It retains non-claims, not a full observation trace. Its stated evidence is fake OPFS plus fake Web Locks; the README says browser-heavy rows are retained evidence rather than fresh execution. No project code was run for this showcase.

The snapshot withholds real browser-matrix coverage, quota/eviction survival, atomic rename, fsync and power-loss durability, and production readiness. Web Locks cancellation of a pending acquisition does not itself cancel provider work after acquisition.

Editorial caution: metadata also retains earlier close-abort and staged-concurrency summaries. The original README and the named guarded-recovery source are the guide to this supplied cut; carried metadata remains unchanged.

The ZIP is preserved separately from its extracted contents. Historical instructions remain inert archival material. No license is added by this guide.
