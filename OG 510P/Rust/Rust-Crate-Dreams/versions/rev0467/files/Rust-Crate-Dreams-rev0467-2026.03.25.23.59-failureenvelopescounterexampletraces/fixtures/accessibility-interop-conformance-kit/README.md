# accessibility-interop-conformance-kit fixtures

Fixture pack for **P-0202 Cross-Platform Accessibility Interop & Conformance Kit**.

This directory is intentionally about the **capture / normalization / interop** layer, not the toolkit-authoring doctor layer.

## Core schema surfaces

- `capture-profile.schema.json` — what was intentionally captured, redacted, and compared
- `normalized-tree.schema.json` — portable semantic tree with per-platform extension lanes
- `event-stream.record.schema.json` — ordered accessibility event records
- `conformance-result.report.schema.json` — scenario verdicts and manual-review markers
- `interop-diff.report.schema.json` — semantic comparison between captures or platform lanes

## Scenarios

### `menu_focus_traversal_cross_platform/`
Same logical menu scenario captured on different platform lanes; useful for checking role/name/focus exposure and honest comparability.

### `virtualized_table_name_regression/`
Release-to-release regression where a virtualized table loses useful accessible names or relations.
