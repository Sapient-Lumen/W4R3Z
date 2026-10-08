# Cargo SBOM Precursor Workbench Kit fixtures

These fixtures are for **P-0125 Cargo SBOM Precursor Workbench Kit**.

The point of this fixture pack is to freeze the support layer **above** Cargo's raw SBOM precursor feature:

- one precursor capture lock,
- one precursor ingest report,
- one capture-route receipt,
- one artifact-coverage report,
- one coverage-ceiling report,
- one normalized build-graph report,
- one transform-loss receipt,
- one diff vocabulary,
- one portable bundle manifest,
- and scenario packs where the hard part is duplicate compilation shape, ambiguous artifact matching, or review-surface drift.

These fixtures should stay distinct from:

- general sidecar attachment contracts,
- trusted publishing / post-publish receipt crates,
- public/private dependency or SemVer witness crates,
- and broad provenance / policy / OCI-distribution systems.

Scenario families in this pass:
- `single_binary_direct_capture/`
- `feature_target_duplicate_compile/`
- `ambiguous_sidecar_association/`


Additional scenario families in this pass:
- `scenarios/direct_build_capture_uses_env_and_stream_routes_without_directory_guessing/`
- `scenarios/rlib_only_member_is_not_missing_precursor_if_output_is_not_eligible/`
- `scenarios/imported_artifact_dir_copy_cannot_prove_same_invocation_generation/`
- `scenarios/portable_bundle_keeps_route_coverage_and_ceiling_separate/`
