# Release-refresh freshness repair rev0835

This audit records a concrete freshness failure found by applying the rev0826-to-rev0834 cumulative patch to a fresh expanded rev0826 tree and then running broader validator discovery.

## Problem found before repair

- `scripts/validate_dedupe_report.py` failed because `DEDUPE_REPORT.md` was stale after cumulative patch application.
- `scripts/validate_rights_readiness.py` failed because `RIGHTS/component_license_ledger.json` was stale after cumulative patch application; newly added scripts had not been counted in the `validators_and_scripts` component.

## Repair

- `scripts/build_dedupe_report.py` now excludes `DEDUPE_REPORT.md` and `SBOM/EvidenceVault-file-inventory.spdx.json`, in addition to `MANIFEST.sha256` and `INDEX/files.*`, to avoid generated-surface count/digest loops.
- `scripts/rebuild_indexes.py` now refreshes `DEDUPE_REPORT.md` after release identity and RO-Crate metadata settle, and before the SPDX inventory is generated.
- The generated freshness surfaces were refreshed after the repair: `DEDUPE_REPORT.md`, `RIGHTS/component_license_ledger.*`, `SBOM/EvidenceVault-file-inventory.spdx.json`, `INDEX/files.*`, `MANIFEST.sha256`, `RELEASE_MANIFEST.json`, and RO-Crate surfaces.

## Live invariants

`scripts/validate_release_refresh_freshness_rev0835.py` checks that:

- `DEDUPE_REPORT.md` exactly matches the current dedupe builder output;
- `RIGHTS/component_license_ledger.json` and `.md` exactly match the current rights-readiness builder output;
- `scripts/rebuild_indexes.py` refreshes dedupe before SPDX;
- SPDX still excludes itself, `MANIFEST.sha256`, and `INDEX/files.*`, while digesting `DEDUPE_REPORT.md`;
- `MANIFEST.sha256` covers both `DEDUPE_REPORT.md` and the SPDX inventory.

This repair does **not** resolve the root rights blocker.
