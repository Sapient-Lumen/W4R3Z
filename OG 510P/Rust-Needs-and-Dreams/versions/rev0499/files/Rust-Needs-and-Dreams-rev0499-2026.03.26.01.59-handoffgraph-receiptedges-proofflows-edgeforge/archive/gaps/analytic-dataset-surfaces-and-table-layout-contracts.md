# Gap: Analytic dataset surfaces and table-layout contracts

## What is missing
Rust now has serious building blocks for columnar analytics and table-formatted data, but it still lacks a **boring, end-to-end contract workflow** for datasets and analytic tables.

Today teams can separately:
- manipulate dataframes in Rust with Polars,
- build query engines and custom analytic systems with DataFusion,
- share columnar in-memory data through Arrow,
- read and write persistent columnar files with Parquet,
- target multiple clouds and local filesystems through `object_store`,
- work with Delta Lake tables through `delta-rs`,
- and increasingly work with Iceberg tables through native Rust implementations.

What is still missing is the shared layer that answers:
- what dataset/table surfaces a project is officially claiming to support,
- which schema + physical-layout facts matter for that claim,
- which engine/runtime combinations were actually checked,
- what row/file/partition-quality evidence exists,
- and how schema/layout/support drift should be reviewed over time.

## Why it matters
This is not just an “analytics framework” problem.

Datasets are increasingly **interfaces**:
- artifacts exchanged between Rust and non-Rust systems,
- long-lived tables consumed by multiple engines,
- feature/training/evaluation inputs for ML systems,
- and operational data products that need compatibility, provenance, and rollout discipline.

Rust’s data stack is no longer just one crate reading CSV files.
It increasingly looks like a toolkit for “deconstructed databases” and composable data systems, where query engines, storage layers, table formats, and object stores are separate components.
That raises the value of a shared review/evidence layer above them.

## Existing building blocks worth composing
- Polars is a DataFrame library for Rust and explicitly builds on Apache Arrow’s memory model.
  https://docs.pola.rs/api/rust/dev/polars/
- Apache Arrow defines a language-independent columnar format and positions itself as a durable foundation for efficient data exchange and analytics.
  https://arrow.apache.org/
  https://arrow.apache.org/blog/2026/02/12/arrow-anniversary/
- DataFusion is an extensible Rust query engine for building analytic systems, with partitioned data sources and custom extension points.
  https://datafusion.apache.org/
- DataFusion explicitly describes itself as part of next-generation “deconstructed database” architectures.
  https://datafusion.apache.org/blog/2025/06/30/cancellation/
- `object_store` provides a uniform Rust API for cloud object stores and local files, explicitly so the same binary can run across clouds and local environments.
  https://docs.rs/object_store
- The Rust Parquet implementation already documents that Arrow and Parquet have different type systems and not every mapping is one-to-one.
  https://docs.rs/parquet/latest/parquet/arrow/index.html
- `delta-rs` is a Rust-based implementation of the Delta Lake protocol with Rust and Python APIs and no dependency on Java/Spark.
  https://delta-io.github.io/delta-rs/
- Iceberg Rust exists as an official native Rust implementation of Apache Iceberg.
  https://rust.iceberg.apache.org/
- The Apache Iceberg implementation-status matrix shows that Rust support is meaningful but still uneven across operations and versions, which is exactly the kind of truth that should become a first-class capability artifact rather than README folklore.
  https://iceberg.apache.org/status/

## Why existing tools are not yet the whole answer
The ecosystem has **format- and engine-specific tools**, but not the **shared contract / capability / evidence layer**:
- Arrow gives a common in-memory model.
- Parquet gives a persistent columnar format.
- Polars and DataFusion execute analytics.
- Delta Lake and Iceberg describe higher-level table semantics.
- `object_store` abstracts remote/local storage.

But teams still have to invent their own answers for:
- stable dataset identities beyond path strings,
- normalized layout/partition/sort/compression declarations,
- cross-engine compatibility claims,
- bounded sample/quality evidence,
- and diffable review artifacts for dataset/table changes.

This is the same ecosystem pattern seen elsewhere in the archive: strong point tools, weak shared artifacts.

## Target outcome
A project should be able to say:
- “this is the dataset/table surface we officially support,”
- “these schema/layout/storage assumptions define that support,”
- “these engines and operations were actually checked,”
- “these samples and invariants justify the claim,”
- and “this is the portable bundle CI, release review, downstream users, and later archaeology can consume.”

That is bigger than a dataframe helper crate and smaller than a new lakehouse platform.
