# Frontier salience snapshot — 2026-03-20 (114)

This pass did **not** open another lakehouse engine, another table format, or another metadata-only evidence workbench.
It deepened **P-0028 open-table-format-kit** by making another product-critical truth explicit:

- **“supports Iceberg / Delta / Hudi” is still too vague unless the crate can say what table surface is exposed, which capabilities are really wired, and how tightly the integration is coupled to specific engine or binding paths.**

## Main judgment

The sharper missing layer is no longer merely “some common traits over multiple open table formats.”
The sharper missing layer is a **crate-authored table-surface / capability-profile / integration-coupling kit**.

The current Rust lakehouse substrate now makes that specific:

1. `iceberg_datafusion` explicitly separates a **catalog-backed provider with automatic metadata refresh** from a **static snapshot provider** for read-only / time-travel style use.
2. `iceberg-rust` 0.9.0 shipped substantive integration churn, including storage refactors, DataFusion 52 upgrades, and an MSRV bump.
3. `deltalake` now publishes a broad support matrix for storage backends and operations including create, read, vacuum, delete, optimize, merge, update, schema evolution, and constraints.
4. `hudi-rs` documents a more read-oriented public surface around snapshot, time-travel, and incremental queries plus DataFusion integration.
5. DataFusion’s foreign table provider FFI helps one compatibility lane, but DataFusion maintainers also say Rust applications using multiple third-party providers still face exact-version coupling pain.
6. Real issues such as the March 2026 Iceberg GCS Python-binding gap show that underlying storage support and binding wiring can diverge in ways that ordinary “supports GCS” claims hide.

That means the next worthy move is not “another universal lakehouse abstraction.”
It is one conservative crate family that can publish:

- **table-surface truth**,
- **capability-profile truth**,
- **integration-coupling truth**,
- **binding-gap truth**,
- and **diffable release-to-release surface changes**.

## Why this beat nearby work

The archive already had adjacent lanes for:

- Iceberg REST / Delta Kernel / UniForm metadata and replay evidence (**P-0359**),
- generic query-engine substrate,
- storage/catalog integration,
- and data contract / schema compatibility work.

What it still lacked was one compact way to say:

- “this provider is live catalog-backed, not a pinned snapshot,”
- “this format path is read-capable and time-travel-capable, but not yet row-level-write-capable,”
- “the storage backend exists below the surface, but this binding path still cannot use it,”
- and “this registration path works, but it is tightly coupled to exact DataFusion versions.”

That is a real receiver-facing product boundary, not just more data-engineering folklore.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still strongest among release-support lanes because release-to-release truth remains broadly under-specified.
3. **P-0017 Trust Lens** — still rising because current registry/advisory substrate makes reviewable trust posture more buildable.
4. **P-0028 open-table-format-kit** — materially stronger after this pass because real Rust lakehouse substrate now exists, but the reviewable contract above it is still missing.
5. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because barrier/phase/aftermath truth cuts across async frameworks.
6. **P-0027 text-input-kit** — still unusually strong because edit-path, geometry, and a11y-mirror truth cut across toolkits.
7. **P-0011 Crate Health Contract Kit** — still very strong because maintainer/support posture remains distinct from trust/risk posture.
8. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.

## What changed in the archive

Added:
- `entries/2026-03-20-294.md`
- `meta/frontier-salience-2026-03-20-114.md`
- `meta/open-table-format-kit-product-plan-2026-03-20.md`
- `meta/open-table-format-kit-lane-boundaries-2026-03-20.md`
- `fixtures/open-table-format-kit/README.md`
- `fixtures/open-table-format-kit/table-surface.receipt.schema.json`
- `fixtures/open-table-format-kit/capability-profile.report.schema.json`
- `fixtures/open-table-format-kit/integration-coupling.receipt.schema.json`
- `fixtures/open-table-format-kit/scenarios/iceberg_catalog_refresh_and_static_snapshot_must_not_share_freshness_claims/`
- `fixtures/open-table-format-kit/scenarios/delta_write_surface_and_hudi_read_surface_must_not_collapse_into_one_common_profile/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/open-table-format-kit.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
