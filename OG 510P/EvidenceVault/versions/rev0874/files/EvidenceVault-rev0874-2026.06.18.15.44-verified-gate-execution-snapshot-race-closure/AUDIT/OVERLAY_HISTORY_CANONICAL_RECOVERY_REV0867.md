# Overlay-history canonical recovery and surface-truth audit — rev0867

## Material recovery, not another registry

Sixteen of the 17 files currently divergent from `INDEX/files.csv` had an exact
canonical version buried in the incremental overlay history. Their only durable
representation was “reverse the right patches in the right order and notice the
matching state.” rev0867 materializes those **16 files / 88,101 bytes** as
content-addressed objects under `RECOVERY/canonical-index/objects/sha256/`.
Every object is admitted only when path, byte count, and SHA-256 all match the
canonical index. `README.md` is the sole same-path mismatch for which reversing
the full incremental history produced no indexed match.

This changes recoverable availability, not current-path truth:

- exact at canonical paths: **100 files / 4,885,267 bytes**;
- additional exact recovery objects: **16 files / 88,101 bytes**;
- total rehydratable: **116 files / 4,973,368 bytes**;
- still unavailable: **4,470 files / 101,448,622 bytes**.

The recovery engine replays history in isolated temporary trees and can
materialize objects only into a separate tree carrying the identical
`INDEX/files.csv`. It does not overwrite, follow symlink ancestry, or mutate
this bundle.

## Severe surface-role defect

Several prominent root files are valid historical canonical evidence but
misleading live-overlay interfaces:

- `RELEASE_MANIFEST.json` still identifies rev0826.
- `SBOM/EvidenceVault-file-inventory.spdx.json` names rev0826 and lists 4,585
  files.
- `MANIFEST.sha256` has 4,588 digest rows.
- `DEDUPE_REPORT.md` says 4,584 files were scanned and points to generator and
  validator scripts absent from this overlay.
- `Makefile` references 47 script paths; 42 are absent.

Rewriting these canonical surfaces would destroy more indexed byte identity.
The correction is therefore operational: `PATCH_BUNDLE_MANIFEST.json` and
`CHECKS/overlay-manifest.json` are the live overlay authorities, and
`scripts/overlay_gate.py` now verifies and reports both at-path coverage and
recovery-object availability. The rev0826 surfaces must not be read as current
archive inventories.

## What remains risky

Publication remains blocked by the missing owner-approved root license/notice.
All 17 selected StreamFold payloads remain absent. The largest technical risk is
still simple byte scarcity: 4,470 indexed files remain unavailable. Further
work should prefer real source acquisition, rights decisions, or elimination of
a false operational surface over additional doctrine.
