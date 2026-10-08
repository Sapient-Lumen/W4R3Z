# Rustdoc JSON Support Contract Kit fixtures

This fixture family exists to keep **P-0051 Rustdoc JSON Support Contract Kit** concrete.

The core claim is that rustdoc JSON should become a **reviewable support contract**, not just a file format and not just a parser API.

## Core review objects

- `source-route.receipt.json`
- `format-window.matrix.json`
- `normalization-loss.report.json`
- `rustdoc-json-support-bundle.manifest.json`

## What these fixtures are trying to protect

They protect against flattening all of the following into one fake verdict:

- rustdoc JSON existed,
- the file parsed,
- a consumer handled this format version,
- the normalized IR preserved the needed facts,
- and downstream semver/docs/support conclusions were therefore safe.

Those are not the same claim.

## Scenario families

### `docsrs_download_keeps_format_version_and_rebuild_gap_explicit/`
A docs.rs JSON import is a real route, but it can involve older `format_version` values and missing coverage for unreached rebuild history.
The fixture keeps source route explicit.

### `rustup_component_for_toolchain_crates_is_not_local_crate_generation/`
`rust-docs-json` for toolchain crates is a real source, but it is not the same support route as generating JSON for a workspace crate with nightly.
The fixture keeps toolchain-doc imports separate from local generation claims.

### `consumer_supports_multiple_format_versions_but_not_every_query/`
A consumer may genuinely support several rustdoc JSON versions while still limiting which normalized queries are trustworthy.
The fixture keeps format-window support separate from downstream query scope.

### `foreign_reexports_and_manifest_semver_need_loss_report/`
Some downstream questions require facts that rustdoc JSON alone does not contain.
The fixture keeps normalization loss and claim ceilings explicit.

### `portable_bundle_keeps_route_window_and_loss_separate/`
A portable bundle should join route, format support, and loss receipts without flattening them into one “supported” bit.
