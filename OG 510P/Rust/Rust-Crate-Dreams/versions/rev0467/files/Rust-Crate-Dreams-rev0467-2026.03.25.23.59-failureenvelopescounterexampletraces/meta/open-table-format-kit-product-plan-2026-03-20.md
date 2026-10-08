# open-table-format-kit — product plan (2026-03-20)

This note sharpens **P-0028 open-table-format-kit** into an implementation-ready `0.1` shape.

## Main judgment

A worthwhile `0.1` should **not** try to become a universal lakehouse engine, a new table format, or a forced “lowest common denominator” trait that pretends Iceberg, Delta, and Hudi are interchangeable.
It should be a **small crate family plus CLI** that helps teams publish one reviewable answer to:

- what table surface they are actually exposing,
- whether that surface is live, pinned, or windowed,
- which operations are honestly supported for that exact adapter/binding,
- which storage/catalog routes are really wired,
- and how tightly the integration is coupled to specific DataFusion / FFI / binding paths.

The missing value is the **boring capability-profile layer** above today’s serious but asymmetric Iceberg / Delta / Hudi implementations.

## What the crate should provide other people

For query-engine maintainers, connector authors, application teams, and platform engineers, the crate should provide:

1. **One table-surface receipt** instead of vague “supports format X” marketing.
2. **One capability-profile report** instead of forcing readers to reconstruct supported reads/writes from scattered docs and issues.
3. **One integration-coupling receipt** instead of hiding exact-version locks or binding wrappers behind successful demos.
4. **Diffable release-to-release surface changes** so upgrades cannot silently change snapshot semantics, provider freshness, or write posture.
5. **A tiny neutral IR** that can sit above format crates without replacing them.

## Three first-class review objects

### 1. Table-surface receipt

Named classes for `0.1` should focus on surface identity and freshness truth such as:

- `catalog_live_refresh`
- `static_snapshot_pin`
- `time_travel_pin`
- `incremental_window`
- `mutable_latest`
- `manual_review_required`

This object should answer:
- whether the subject is resolved by catalog identifier, metadata path, or base table URI,
- whether readers should expect automatic refresh or pinned metadata,
- whether the surface is read-only, latest-view, or explicit time-windowed,
- and what provider surface is actually being exported (`native_table_api`, `datafusion_table_provider`, `ffi_table_provider`, `python_binding_wrapper`, etc.).

### 2. Capability-profile report

Named classes for `0.1` should focus on operation truth such as:

- `snapshot_read_supported`
- `time_travel_supported`
- `incremental_read_supported`
- `datafusion_registration_supported`
- `row_level_dml_supported`
- `maintenance_ops_supported`
- `binding_gap`
- `manual_review_required`

This object should answer:
- which read modes are implemented,
- which write/maintenance operations are implemented,
- whether the capability is native, adapter-specific, binding-only, or still absent,
- and which capabilities are intentionally downgraded when crossing formats or bindings.

### 3. Integration-coupling receipt

Named classes for `0.1` should focus on engine/binding compatibility truth such as:

- `datafusion_exact_version_match_required`
- `ffi_table_provider_decoupled`
- `native_only_no_shared_engine_contract`
- `language_binding_wrapper`
- `binding_storage_gap`
- `manual_review_required`

This object should answer:
- whether the integration requires an exact shared crate-graph version of DataFusion,
- whether FFI loosens that coupling,
- whether the path is Rust-native only or mediated through a language binding,
- and whether storage/catalog support exists below the surface but is not yet wired in the exported path.

## Recommended `0.1` command surface

### `cargo otf capture <subject>`
Import a table handle / provider / config and emit:
- `table-surface.receipt.json`
- `capability-profile.report.json`
- `integration-coupling.receipt.json`

### `cargo otf doctor`
Run consistency checks and classify:
- `surface_capability_mismatch`
- `binding_gap_detected`
- `freshness_claim_too_broad`
- `version_coupling_detected`
- `manual_review_required`

### `cargo otf diff <old> <new>`
Compare two captures and emit:
- `surface_changed`
- `capability_changed`
- `coupling_changed`
- `storage_route_changed`
- `manual_review_boundary_changed`

### `cargo otf bundle`
Produce one compact `.otfbundle.zip` containing reports, summaries, and fixture references.

## Recommended crate/workspace split

- `otf_model`
  - shared IR for table surfaces, capabilities, coupling, and diffs
- `otf_capture`
  - capture helpers for native table handles, providers, and config imports
- `otf_iceberg`
  - Iceberg / Iceberg DataFusion adapters
- `otf_delta`
  - Delta Lake adapters
- `otf_hudi`
  - Hudi adapters
- `otf_check`
  - consistency rules and downgrade detection
- `cargo-otf`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `otf_datafusion`
- `otf_python_bridge`
- `otf_catalog_rest`
- `otf_object_store`

## `0.1` artifact set

Core artifacts should be:
- `otf.toml`
- `table-surface.receipt.json`
- `capability-profile.report.json`
- `integration-coupling.receipt.json`
- `otf-check.report.json`
- `otf-diff.report.json`
- `notes.md`

The MVP should make these three truths reviewable before it tries to grow into a universal adapter layer:
- table-surface truth,
- capability-profile truth,
- integration-coupling truth.

## Discovery order

1. **Subject identity import**
   - catalog identifier vs metadata path vs base URI
   - format family
   - provider surface
2. **Freshness classification**
   - live refresh vs static snapshot vs time-travel pin vs incremental window
3. **Capability capture**
   - snapshot reads
   - time travel
   - incremental reads
   - engine registration
   - write / maintenance operations
4. **Storage and catalog wiring**
   - cloud/object store schemes
   - REST catalog paths
   - binding or adapter gaps
5. **Integration coupling**
   - exact version match requirements
   - FFI vs native trait coupling
   - binding wrappers and drift zones
6. **Diff + bundle**
   - capability drift
   - freshness drift
   - coupling drift
   - compact repro archive

## Ranking discipline

Do **not** let future passes sell this as:
- a universal lowest-common-denominator trait,
- a replacement for Iceberg / Delta / Hudi crates,
- a metadata-only workbench (that belongs closer to **P-0359**),
- or a generic DataFusion plugin story.

The sharper missing value is the **receiver-facing support contract** for what table surface, operation surface, and integration coupling another team is actually being asked to depend on.
