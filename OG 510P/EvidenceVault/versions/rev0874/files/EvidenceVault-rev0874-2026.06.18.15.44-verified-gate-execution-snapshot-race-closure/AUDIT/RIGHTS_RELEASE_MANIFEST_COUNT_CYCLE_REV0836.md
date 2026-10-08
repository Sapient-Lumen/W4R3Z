# Rights release-manifest count-cycle repair rev0836

- Status: `rights_release_manifest_count_cycle_repaired`
- Risk: `RIGHTS/component_license_ledger.json` counted `RELEASE_MANIFEST.json` bytes even though `scripts/rebuild_indexes.py` rebuilt rights readiness before refreshing release-manifest identity fields.
- Repair: `scripts/build_rights_readiness.py` now excludes `RELEASE_MANIFEST.json` from rights byte counts, alongside `MANIFEST.sha256` and `INDEX/files.*`.

This keeps the rights ledger focused on rights conclusions instead of release-identity byte churn.

Validated by `scripts/validate_rights_release_manifest_cycle_rev0836.py`.
