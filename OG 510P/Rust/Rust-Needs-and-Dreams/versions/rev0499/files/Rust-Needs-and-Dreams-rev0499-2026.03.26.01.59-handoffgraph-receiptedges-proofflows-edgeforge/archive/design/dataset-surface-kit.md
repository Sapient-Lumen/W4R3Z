# Design: Dataset Surface Kit (`cargo datasetcheck`, `dataset-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust project’s supported analytic dataset/table surface: dataset identity, schema attachments, physical layout, storage/catalog assumptions, engine compatibility posture, checked samples, and data-quality evidence.

This should **not** replace Polars, DataFusion, Arrow, Parquet, `object_store`, Delta Lake, Iceberg, dbt-style workflows, or hosted catalog/governance products.
It should make them compose better and make support claims reviewable.

## References (signals)
- Polars is a DataFrame library for Rust and is based on Apache Arrow’s memory model.
  https://docs.pola.rs/api/rust/dev/polars/
- Apache Arrow defines a language-independent columnar format for efficient analytic operations and now frames itself as a durable ecosystem foundation.
  https://arrow.apache.org/
  https://arrow.apache.org/blog/2026/02/12/arrow-anniversary/
- DataFusion is an extensible query engine written in Rust that uses Apache Arrow as its in-memory format and is aimed at developers building data-centric systems.
  https://datafusion.apache.org/
- DataFusion explicitly calls itself part of next-generation “deconstructed database” architectures.
  https://datafusion.apache.org/blog/2025/06/30/cancellation/
- `object_store` exposes a uniform API across cloud object stores and local files.
  https://docs.rs/object_store
- The Rust Parquet implementation documents non-trivial Arrow↔Parquet type mapping differences.
  https://docs.rs/parquet/latest/parquet/arrow/index.html
- `delta-rs` is a Rust-native Delta Lake implementation.
  https://delta-io.github.io/delta-rs/
- Iceberg Rust is an official native Rust implementation of Apache Iceberg.
  https://rust.iceberg.apache.org/
- The Apache Iceberg status matrix shows that implementation support differs meaningfully by operation/version/runtime, which strengthens the case for explicit capability reports instead of vague “Iceberg supported” claims.
  https://iceberg.apache.org/status/

## Core components

### 1) `dataset-surface/v0`
A design-time declaration of the supported data boundary for a crate/binary/workspace.

Required ideas:
- stable dataset/table identity
- boundary kind:
  - single file
  - directory-partitioned dataset
  - table-format-backed table
  - logical exported dataset view
- intended consumers:
  - internal pipeline
  - external customers/partners
  - BI/analytics
  - ML training/eval
  - test fixture / benchmark fixture
- freshness/update posture:
  - immutable snapshot
  - append-only
  - slowly changing
  - mutable latest-view
- support class:
  - official
  - best-effort
  - experimental
  - deprecated
  - internal
- optional ownership / producer metadata
- optional retention / snapshot-window notes

This is the thing humans review before trusting automation.

### 2) `dataset-layout-profile/v0`
A machine-readable description of the layout and storage semantics that matter for interoperability.

Required ideas:
- logical schema attachment references:
  - Arrow schema
  - Parquet schema metadata
  - Delta/Iceberg table metadata
  - linked Schema Contract ids where useful
- file/table format families:
  - Arrow IPC / Feather
  - Parquet
  - CSV / JSON as adapters in v0
  - Delta Lake
  - Iceberg
- partition spec / partition transforms
- sort order / clustering hints
- compression / encoding posture where relevant
- nullability / timezone / decimal / nested-type notes where needed
- object-store / catalog assumptions:
  - local fs
  - S3-compatible
  - GCS
  - Azure Blob/ADLS
  - REST/sql/hive-style catalog attachments where applicable
- snapshot/versioning posture where table formats provide it
- deletion/update semantics when present
- statistics/manifests sidecar posture where relevant

Design rule: preserve raw format truth and attach source metadata artifacts rather than flattening Arrow, Parquet, Delta, and Iceberg into one fake canonical format.

### 3) `engine-capability-profile/v0`
A declaration of which readers/query engines/runtime lanes are in scope and what operations they are expected to support.

Required ideas:
- engine/runtime identifiers (for example: Polars lazy, DataFusion SQL/DataFrame, Parquet reader, Delta Rust, Iceberg Rust)
- read / write / scan / projection / predicate / partition-pruning / streaming / snapshot lanes as relevant
- support classes per engine lane:
  - official
  - checked subset
  - experimental
  - read-only
  - unsupported
- version or capability-baseline references
- known unsupported types/operations/features
- optional scale notes (sample-only, bounded-size, cloud-only, local-only)

This is how the kit stays honest when implementation support is partial.

### 4) `sample-catalog/v0`
Small canonical sample evidence.

Potential contents:
- example rows / batches / files
- partition examples
- edge-case rows for nullability / decimals / timestamps / nesting
- negative samples expected to fail validation or compatibility checks
- labels:
  - illustrative only
  - generated
  - checked in CI
  - captured fixture

Design rule: keep samples small, stable, and privacy-safe. Do not turn the pack into a data dump.

### 5) `dataset-check-plan/v0`
A concrete declaration of what is checked.

Required ideas:
- extraction sources: schema metadata / manifests / catalog / filesystem inventory / query-engine introspection
- selected engines/runtimes/profiles
- selected storage backends or fixtures
- checks performed:
  - schema extraction
  - layout extraction
  - engine compatibility checks
  - roundtrip / read/write checks
  - partition/sort/layout drift checks
  - sample validation
  - row/file/partition invariants
  - statistics/manifest consistency checks where relevant
- intentionally omitted lanes and why

This is where the kit stops pretending “it loaded once” means “the dataset surface is reviewed.”

### 6) `dataset-check-report/v0`
Evidence from extraction, compatibility checks, and quality checks.

Possible contents:
- extracted schema/layout summary
- engine pass/fail summary by lane
- unsupported feature findings
- Arrow↔Parquet / table-format mismatch findings
- partition/layout drift findings
- invariant/quality outcomes
- sample validation outcomes
- linked raw artifacts: Arrow schemas, Parquet metadata dumps, Delta/Iceberg metadata snapshots, file inventories, query plans, and engine logs

### 7) `dataset-diff-report/v0` (optional)
For compatibility-sensitive change review:
- column added/removed/renamed
- data type / nullability / timezone / decimal precision changes
- partition-spec or sort-order changes
- compression/encoding changes that affect support posture
- table-format protocol/version changes
- engine support widened/narrowed
- support class changed
- snapshot-window or retention posture changed

Should distinguish:
- additive changes
- compatibility-sensitive changes
- layout-only drift
- support-surface regressions
- documentation-only updates

### 8) `dataset-pack/v0`
Bundle format containing:
- `dataset-surface/v0`
- `dataset-layout-profile/v0`
- `engine-capability-profile/v0`
- optional `sample-catalog/v0`
- one or more `dataset-check-report/v0`
- optional `dataset-diff-report/v0`
- optional raw attachments: Arrow schemas, Parquet metadata, Delta/Iceberg table metadata, catalog exports, sample fixtures, and engine-specific reports

This is the unit that should travel through CI, release review, reproducibility work, and later archaeology.

### 9) `cargo datasetcheck`
Reference UX:
- `cargo datasetcheck init`
- `cargo datasetcheck inspect`
- `cargo datasetcheck engines`
- `cargo datasetcheck samples`
- `cargo datasetcheck diff`
- `cargo datasetcheck pack`

`cargo datasetcheck` should begin as an adapter / explainer / packer.
It should not pretend to be the one true query engine, catalog, or governance platform.

## Default policy
- **Separate logical schema, physical layout, engine capability, and checked evidence.**
- **Preserve raw format truth** from Arrow/Parquet/Delta/Iceberg/object-store/catalog sources instead of flattening everything into one fake data model.
- **Treat engine/runtime support as an explicit capability surface, not an implied consequence of “uses Arrow.”**
- **Keep checked samples distinct from illustrative examples** so docs remain honest.
- **Prefer bounded evidence** (sample fixtures, metadata snapshots, targeted invariants) over giant exported datasets.
- **Make storage/catalog assumptions explicit** whenever they materially affect support.

## What the kit should provide to others
- **Schema Contract Kit:** attach dataset-oriented logical schema artifacts without absorbing layout/storage semantics into generic API-schema workflows.
- **Database Contract Kit:** complement live database schema/query/migration contracts with offline/table-format dataset contracts rather than blurring OLTP and analytic-lake surfaces together.
- **Model Surface Kit:** declare and validate training/eval/feature dataset assumptions without turning models into data-governance products.
- **Support Envelope Kit:** record which storage backends, runtime environments, and engine baselines are officially supported.
- **Repro Build / Perf / Footprint work:** attach dataset fixtures and layout assumptions to performance/repro workflows without making those kits own the dataset contract.

## Overlap boundaries
- **Not another dataframe or query engine:** Polars, DataFusion, DuckDB adapters, and similar tools remain the execution layer.
- **Not another table format:** Delta Lake and Iceberg remain the format/protocol truth.
- **Not Schema Contract Kit:** generic machine-readable schemas stay separate; this kit is about the composed dataset/table boundary, including layout/storage/engine support.
- **Not Database Contract Kit:** live SQL schemas, migration execution, and ephemeral databases remain there.
- **Not Model Surface Kit:** model/tokenizer/runtime packaging remains separate even when models consume datasets.
- **Not a hosted catalog/governance product:** the value is the portable artifact and review workflow, not another control plane.

## Hard problems (explicitly scoped)
1. **Logical schema is not the whole interface**
   - partition specs, sort order, compression, snapshots, and object-store/catalog assumptions often matter just as much.
2. **Arrow does not erase every format mismatch**
   - Parquet/Arrow conversions and table-format semantics have real edge cases that v0 must preserve, not hand-wave away.
3. **Implementation support is partial and moving**
   - especially for richer table-format features; capability profiles must stay explicit.
4. **Quality checks can sprawl without discipline**
   - v0 should favor bounded invariants and sample evidence over turning into an all-purpose data-observability platform.
5. **Credentials and governance are adjacent but distinct**
   - this kit should reference storage/catalog access posture, not own secret-management or enterprise governance policy.
