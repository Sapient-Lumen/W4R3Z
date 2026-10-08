# Scenario: cargo-semver-checks JSON imported natively while release-note prose stays summary-only

This fixture freezes the distinction between **native tool import truth** and later human summary.

The lane uses:
- verbatim `cargo-semver-checks` JSON as the canonical machine import for the public-API hazard slice,
- normalized `cargo fix` output as fixup evidence,
- `cargo metadata` as the workspace/package-scope anchor,
- and a maintainer-authored release summary as advisory prose only.

The point is that the pack must say **which facts came from native tool surfaces** and **which facts were only summarized later**.
It must not let a release-note paragraph replace the imported receipts.
