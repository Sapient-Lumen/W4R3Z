# Cargo Package Review Kit fixtures

These fixtures are for **P-0470 Cargo Package Review Kit**.

The point is to freeze the layer above raw `cargo package` output:

- workspace candidate-set reports,
- manifest-normalization reports,
- path explanations,
- packaged-surface receipts,
- archive-authority reports,
- extraction-mutation reports,
- package policy warnings,
- and diffable review bundles.

These fixtures should stay distinct from:

- trusted-publishing rehearsal bundles,
- post-publish receipt joins,
- provenance attestations,
- SBOM precursor capture,
- and general artifact-sidecar attachment contracts.

Scenario families in this pass:
- `authored_manifest_and_packaged_manifest_must_not_share_same_hash_basis/`
- `extracted_verification_tree_adds_cargo_ok_and_mtime_drift_after_unpack/`
- `workspace_interdependent_candidates/`
- `external_license_and_readme_copyin/`
- `subdir_package_dirty_vcs_snapshot/`
- `generated_asset_budget_warning/`
