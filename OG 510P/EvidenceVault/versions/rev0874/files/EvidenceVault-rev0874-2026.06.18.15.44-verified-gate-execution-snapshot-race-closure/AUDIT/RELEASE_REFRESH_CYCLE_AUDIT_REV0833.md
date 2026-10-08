# Release refresh cycle audit rev0833

This audit records the rev0833 repair for generated material surfaces that need to survive the normal release refresh path.

- Status: `release_refresh_cycle_repaired`
- Risk: Generated rights and SPDX surfaces could validate immediately after patch application but become stale or impossible to close after the normal release refresh rebuilt archive manifest/index surfaces.
- Repair: rebuild_indexes.py now refreshes cycle-safe material audit, rights, and SBOM builders before final INDEX/MANIFEST emission; SPDX and rights byte-count ledgers exclude generated digest/index files that would otherwise create a self-description cycle.

## Cycle-breaking exclusions

| Surface | Excluded paths | Reason |
| --- | --- | --- |
| `SBOM/EvidenceVault-file-inventory.spdx.json` | `INDEX/files.csv`, `INDEX/files.json`, `MANIFEST.sha256`, `SBOM/EvidenceVault-file-inventory.spdx.json` | The manifest and index describe the SPDX file, so the SPDX file must not digest those generated self-description surfaces. |
| `RIGHTS/component_license_ledger.json` | `INDEX/files.csv`, `INDEX/files.json`, `MANIFEST.sha256`, `RELEASE_MANIFEST.json` | Rights conclusions are unaffected by generated release-manifest/index byte counts; counting them made the ledger stale after a normal rebuild. |

## Material refresh builders

- `scripts/build_upstream_retention_coverage.py`
- `scripts/build_absolute_path_reference_audit.py`
- `scripts/build_path_reference_shape_audit.py`
- `scripts/build_rights_evidence_scan.py`
- `scripts/build_license_reference_integrity_audit.py`
- `scripts/build_rights_readiness.py`
- `scripts/build_spdx_inventory.py`

## Post-repair invariants

- MANIFEST.sha256 covers SBOM/EvidenceVault-file-inventory.spdx.json
- SBOM/EvidenceVault-file-inventory.spdx.json does not digest itself, MANIFEST.sha256, INDEX/files.json, or INDEX/files.csv
- RIGHTS/component_license_ledger.json does not byte-count RELEASE_MANIFEST.json, MANIFEST.sha256, or INDEX/files.*
- scripts/rebuild_indexes.py refreshes material audit, rights, and SBOM surfaces before final INDEX/MANIFEST emission
- a repeated rebuild_indexes.py run is idempotent over AUDIT, RIGHTS, SBOM, and scripts material surfaces

Validated by `scripts/validate_release_refresh_cycle_rev0833.py`.
