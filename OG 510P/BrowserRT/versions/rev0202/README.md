# archive rev0202: linked recovery-guidance table refactor

Archive label and linked revision: **rev0202**. Packaged runtime remains **rev0125 / 0.0.125**. Filename date: **2026-07-08**. Preserved extracted files: **1,330**.

[Original ZIP](BrowserRT-rev0202-2026.07.08.22.46-runtime-core-recovery-guidance-table-ratchet.zip) · [Original README](contents/README.md) · [Start here](contents/START_HERE.md) · [Linked revision receipt](contents/REV0202-LINKED-REVISION-RECEIPT.json) · [Project index](../../README.md)

## Why this snapshot matters

The [first-read work note](contents/docs/00-meta/cloudtainer-forward-momentum-rev0202-2026-07-08-runtime-core-recovery-guidance-table-ratchet.md) describes a refactor of storage-recovery guidance into compact classification and recovery-step tables. The [implementation](contents/src/browser-storage-recovery-guidance.mjs) contains those tables; the [runtime-core audit source](contents/tools/runtime_core_entry_contract_audit.mjs) carries the tightened source-closure budget.

The [supplied refactor receipt](contents/artifacts/datacube-audit/REV0125-RUNTIME-CORE-RECOVERY-GUIDANCE-TABLE-RATCHET-REV0202.json) reports runtime-core bytes falling from 129,576 to 128,028 while its limit falls from 130,000 to 128,500. It also records package-boundary and storage-posture checks as passed. These figures and comparisons are carried historical measurements; rev0201 is not one of the five separately supplied snapshots, and those checks were not rerun for this showcase.

## Read the two identities together

The [package metadata](contents/package.json), [CUBE-META](contents/CUBE-META.json), and [runtime receipt](contents/REVISION-RECEIPT.json) retain rev0125 / 0.0.125 while identifying linked rev0202. The separate linked receipt makes the relationship explicit. This archive is not evidence of a runtime-version promotion or an npm publication.

Some `summary` fields still reference linked rev0174. The direct rev0202 README, work note, linked-revision fields, and linked receipt identify the supplied cut; these older fields are preserved rather than silently reconciled.

The original documents withhold production readiness, a runtime promotion, privacy/fingerprinting mitigation, quota reservation, eviction survival, fsync or power-loss durability, Web Locks fairness, Service Worker lifetime guarantees, browser-kill/crash recovery, and cross-browser proof.

The ZIP is preserved separately from its extracted contents. Historical instructions remain inert archival material. No license is added by this guide.
