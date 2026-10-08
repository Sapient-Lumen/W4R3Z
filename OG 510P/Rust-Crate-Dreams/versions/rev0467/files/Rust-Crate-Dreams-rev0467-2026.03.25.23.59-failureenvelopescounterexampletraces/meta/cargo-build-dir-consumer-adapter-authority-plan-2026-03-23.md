# P-0489 — Cargo Build-Dir Consumer Transition Kit: consumer need, adapter authority, windowed viability, and rehearsal bundles (2026-03-23)

This note sharpens **P-0489** into a more reviewable product.

## Main judgment

A good build-dir transition crate should now publish four receiver-facing truths separately:
1. **consumer need** — what outcome the workflow actually needs;
2. **adapter authority** — what source class justifies the suggested route;
3. **windowed viability** — which Cargo / channel / layout windows the route really covers;
4. **rehearsal bundle inventory** — how those claims travel together with inventories, audits, and transition receipts.

That is the difference between a migration suggestion and a durable support artifact.

## Product stance

The crate should stay small and migration-first.
It should not try to become:
- a stable filesystem abstraction for Cargo internals,
- a Cargo-internals library,
- a code-rewrite engine,
- or an organization-wide policy registry for every Cargo workflow.

It should instead emit a compact bundle another maintainer or CI owner can answer with:
- what the consumer really needed,
- which official source justifies the suggested adapter,
- which Cargo/layout window that claim actually covers,
- and where fallback or manual review still begins.

## New first-class artifacts

### `consumer-need.report.json`
Suggested fields:
- `schema_version`
- `consumer_ref`
- `observed_path_pattern`
- `need_class`
- `claimed_need`
- `confidence`
- `misclassification_risk`
- `evidence[]`
- `notes`

### `adapter-authority.receipt.json`
Suggested fields:
- `schema_version`
- `consumer_ref`
- `recommended_adapter`
- `source_class`
- `authority_basis[]`
- `claim_scope`
- `applies_from_cargo`
- `applies_on_channel`
- `notes`

### `windowed-viability.matrix.json`
Suggested fields:
- `schema_version`
- `consumer_ref`
- `rows[]`
  - `window_label`
  - `cargo_channel`
  - `cargo_version_floor`
  - `layout_mode`
  - `verdict`
  - `fallback_posture`
  - `notes`

### `rehearsal-support-bundle.manifest.json`
Suggested fields:
- `schema_version`
- `bundle_kind`
- `subject`
- `compared_modes[]`
- `receipts[]`
  - `kind`
  - `path`
  - `purpose`
- `share_safe`

## CLI sketch

- `cargo build-dir-transition classify` — infer consumer need from observed path-coupled behavior
- `cargo build-dir-transition authority` — attach authority classes to adapter claims
- `cargo build-dir-transition matrix` — emit Cargo/channel/layout window rows
- `cargo build-dir-transition bundle` — pack the need + authority + viability + transition bundle

## Good proving grounds

1. a test helper that really wants a binary and should be routed to `CARGO_BIN_EXE_*` with a version window;
2. a build helper that claims to want target-dir but really only owns build-script output;
3. a user-requested artifact lookup that still crosses into upstream-gap/manual-review territory;
4. a migration rehearsal bundle that compares legacy layout, custom `build.build-dir`, and `-Zbuild-dir-new-layout` observations.

## Sources

- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- https://doc.rust-lang.org/cargo/reference/build-cache.html
- https://doc.rust-lang.org/cargo/commands/cargo-build.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
