# Cargo Build Script Delegation Kit fixtures

These fixtures are for **P-0508 Cargo Build Script Delegation Kit**.

The point of this pack is to freeze the review layer above evolving Cargo build-script substrate:

- named build-unit topology,
- per-unit output lanes,
- override authority,
- unstable bridge posture,
- and release-to-release delegation drift.

These fixtures should stay distinct from:

- buildscript diagnostics bundles,
- hermetic buildscript replay tests,
- target-support receipts,
- native dependency policy kits,
- and pure artifact-dependency adoption bundles.

Scenario families in this pass:
- `multiple_build_scripts_need_named_output_lanes/`
- `links_override_is_authoritative_without_live_run/`
- `delegate_upgrade_reorders_units_and_changes_support_story/`
- `artifact_bridge_requires_collision_authority/`
