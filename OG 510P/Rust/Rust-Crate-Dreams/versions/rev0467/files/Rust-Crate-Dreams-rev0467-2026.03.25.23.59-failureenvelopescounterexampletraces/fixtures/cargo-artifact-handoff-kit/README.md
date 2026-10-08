# Cargo Artifact Handoff Kit fixtures

These fixtures are for **P-0471 Cargo Artifact Handoff Kit**.

The point is to freeze the layer above raw Cargo build output:

- promoted artifact manifests,
- artifact-origin receipts,
- handoff receipts with optional session linkage,
- and diffable layout/output change bundles.

These fixtures should stay distinct from:

- build-dir consumer transition bundles,
- sidecar association / shipping-policy bundles,
- SBOM precursor normalization bundles,
- and publish-identity or post-publish receipt joins.

Scenario families in this pass:
- `single_binary_copied_out/`
- `workspace_multi_profile_split/`
- `build_script_uplift_manual_review/`
- `imported_session_link/`
