# Cargo Artifact Sidecar Contract Kit fixtures

These fixtures are for **P-0479 Cargo Artifact Sidecar Contract Kit**.

The point of this fixture pack is to freeze the support layer **above** raw artifact output and **beside** SBOM precursor-specific normalization:

- one sidecar contract lock,
- one artifact↔sidecar index,
- one sidecar schema/stability report,
- one attachment-policy receipt,
- one association-exactness receipt,
- and one sidecar-surface diff vocabulary.

These fixtures should stay distinct from:

- broader artifact handoff manifests,
- SBOM precursor normalization and transform-loss reports,
- trusted publishing / post-publish receipt crates,
- and debugger-support or docs.rs support contracts.

Scenario families in this pass:
- `single_binary_ship_with_sbom_and_pdb/`
- `multi_artifact_split_sidecars/`
- `schema_version_drift/`
- `missing_expected_sidecar_manual_review/`
