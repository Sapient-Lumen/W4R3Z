# Epic proposal: Dataset Surface Kit

## Thesis
Rust’s columnar/data-systems ecosystem is mature enough that the missing contribution is no longer “yet another dataframe crate” or “yet another lakehouse wrapper.”
The higher-leverage missing piece is a **portable dataset-surface contract** that lets teams declare, diff, validate, and ship what a dataset/table actually promises: identity, schema attachments, physical layout, storage/catalog assumptions, engine compatibility posture, checked samples, and quality evidence.

In other words: Rust needs a boring, attachable `dataset-pack/v0` more than it needs one more execution engine pretending interoperability is already solved.

## Why now
The ecosystem signals line up:
- Polars is already a serious Arrow-based dataframe library in Rust.
- DataFusion is now a major Rust query-engine toolkit and explicitly part of “deconstructed database” architectures.
- Arrow has become a durable multi-language foundation for columnar interoperability.
- Rust-native Delta Lake and Iceberg implementations now exist.
- `object_store` makes multi-cloud/local data access a normal Rust workflow.
- The hard part is increasingly not “can Rust touch this data?” but “what exactly is this dataset/table promising and what was actually checked?”

Sources:
- https://docs.pola.rs/api/rust/dev/polars/
- https://datafusion.apache.org/
- https://datafusion.apache.org/blog/2025/06/30/cancellation/
- https://arrow.apache.org/
- https://arrow.apache.org/blog/2026/02/12/arrow-anniversary/
- https://delta-io.github.io/delta-rs/
- https://rust.iceberg.apache.org/
- https://docs.rs/object_store
- https://iceberg.apache.org/status/

## What should be built
A first credible version should ship:
1. `dataset-surface/v0`, `dataset-layout-profile/v0`, `engine-capability-profile/v0`, `sample-catalog/v0`, `dataset-check-plan/v0`, `dataset-check-report/v0`, optional `dataset-diff-report/v0`, and `dataset-pack/v0`
2. adapters for common Rust data lanes (Arrow schemas, Parquet metadata, Polars/DataFusion checks, Delta/Iceberg metadata snapshots, `object_store`-backed fixtures)
3. docs/reference generation for declared dataset surfaces, supported engines, layout/storage assumptions, and checked sample evidence
4. validation/reporting support for schema/layout drift, engine-compatibility narrowing, and bounded dataset-quality/invariant checks
5. examples showing dataset packs attached to release review, analytic pipelines, benchmark fixtures, and model/data workflows

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one local Parquet + Arrow + Polars dataset with stable schema/layout/sample evidence
- one DataFusion + `object_store` pilot that proves storage assumptions and engine compatibility belong in the surface contract
- one `delta-rs` pilot with snapshot/layout metadata attachments and compatibility drift checks
- one Iceberg Rust pilot where capability profiles are especially important because support is partial and evolving

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve dataset identity, layout profile, and engine-capability truth as separate artifacts
2. **v0.2 adapters**
   - support Arrow schemas, Parquet metadata, Polars/DataFusion checks, Delta metadata, Iceberg metadata, and `object_store` fixture references
3. **v0.3 cross-kit integration**
   - integrate with Schema Contract, Model Surface, Support Envelope, Perf Labs, and Repro Build workflows
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one exact engine/format stack

## Success metrics
- Teams can review dataset/table changes as explicit artifacts instead of path diffs, ad hoc notebooks, and prose.
- Engine support becomes more honest because supported subsets and unchecked lanes are explicit.
- Arrow/Parquet/table-format/storage assumptions stay attached to the dataset instead of being scattered across docs and CI.
- Dataset fixtures become easier to reuse across analytics, performance, and ML workflows.
- Rust data systems become easier to hand off across teams and across languages because the support surface is no longer implicit.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Schema Contract Kit covers generic machine-readable schemas,
- Database Contract Kit covers live database evolution,
- Model Surface Kit covers model/tokenizer/runtime packaging,
- Support Envelope Kit covers platform/runtime baselines,
- and Service/Event Surface Kits cover online interfaces.

But none of those is the portable contract for the **dataset/table boundary itself**.
Dataset Surface Kit is the missing substrate that keeps schema, layout, storage, engine support, and sample evidence attached to one reviewable data interface without absorbing them into one mega-format.
