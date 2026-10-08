# Frontier salience snapshot — 2026-03-20 (124)

This pass did **not** open another Cargo lane, another schema parser, or another registry product.
It deepened **P-0124 schema-compatibility-workbench-kit** by making a more boring and more reusable boundary explicit:

- **a team can truthfully say “no breaking schema changes” while still leaving other teams unable to tell what exact surfaces were compared, what compatibility profile defined “breaking”, how strong the findings were, and which ignores or waivers made the gate green.**

## Main judgment

The sharper missing layer is no longer merely “a diff tool for schemas”.
The sharper missing layer is a **comparison-basis / compatibility-profile / finding-strength / policy-decision contract**.

Current schema tooling makes that specific:

1. Buf already turns Protobuf compatibility into a configurable review surface with `FILE`, `PACKAGE`, `WIRE_JSON`, and `WIRE` categories.
2. oasdiff already distinguishes definite (`ERR`) versus potential (`WARN`) breaking changes and allows ignore files plus fail thresholds.
3. Rust’s `jsonschema` crate already gives standards-aware validation and structured reports, but validation is not one universal compatibility verdict.
4. Confluent’s Schema Registry docs and API are explicit that compatibility results depend on subject/global mode, latest-only versus transitive history, optional normalization, and optional verbose reasons.
5. Schemars already derives schemas from Rust types while respecting serialization meaning, so even “generated schema diff” has a real basis story.
6. The Rust `schema-registry-compatibility` crate already proves there is real native compatibility substrate, including seven compatibility modes, but not one shared receiver-facing contract above it.

That means the next worthy move is not another engine.
It is one conservative crate family that can publish:

- **comparison-basis truth**,
- **compatibility-profile truth**,
- **finding-strength truth**,
- and **policy-decision truth**.

## Why this beat nearby work

The archive already had adjacent lanes for:

- registry/data-contract workflows,
- persisted-data migration,
- generic OpenAPI/JSON Schema toolchains,
- and public API release-review work.

What it still lacked was one compact way to say:

- “this result is latest-only, not transitive,”
- “this green check is wire-compatible, not source-compatible,”
- “this warning is potential, not mechanically definite,”
- and “this gate passed only because these findings were ignored or waived.”

That is a real receiver-facing product boundary, not just another parser or diff engine.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because release-to-release truth remains broadly under-specified.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and timeout aftermath truth remain broad pain points.
4. **P-0523 Crate Test Surface Pack Kit** — still unusually strong because downstream test-support truth remains under-served.
5. **P-0124 schema-compatibility-workbench-kit** — materially stronger after this pass because schema engines now exist, but one shared review contract above them still does not.
6. **P-0017 Trust Lens** — still unusually strong because reviewable trust posture is newly more buildable.
7. **P-0039 i18n-icu-kit** — stronger after the latest contract pass, but still best when kept runtime-contract-focused.
8. **P-0121 ffi-boundary-conformance-kit** — still important and now sharper, but should remain boundary-contract-first rather than absorbing broader schema/API review work.

## What changed in the archive

Added:
- `entries/2026-03-20-304.md`
- `meta/frontier-salience-2026-03-20-124.md`
- `meta/schema-compatibility-workbench-product-plan-2026-03-20.md`
- `meta/schema-compatibility-workbench-lane-boundaries-2026-03-20.md`
- `fixtures/schema-compatibility-workbench-kit/README.md`
- `fixtures/schema-compatibility-workbench-kit/comparison-basis.receipt.schema.json`
- `fixtures/schema-compatibility-workbench-kit/compatibility-profile.receipt.schema.json`
- `fixtures/schema-compatibility-workbench-kit/finding-strength.report.schema.json`
- `fixtures/schema-compatibility-workbench-kit/policy-decision.report.schema.json`
- scenario families for latest-only versus transitive history, warning-level versus definite breakage, validation-only versus compatibility, and wire versus generated-source profiles

Updated:
- `README.md`
- `INDEX.md`
- `proposals/schema-compatibility-workbench-kit.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy schema-compatibility contribution for Rust should now provide more than diff output and CI exit codes.
It should provide:

- one explicit **comparison-basis receipt**,
- one explicit **compatibility-profile receipt**,
- one explicit **finding-strength report**,
- and one honest **policy-decision report**.

## Freshness anchors

- Buf breaking change detection — https://buf.build/docs/breaking/
- oasdiff breaking changes docs — https://github.com/oasdiff/oasdiff/blob/main/docs/BREAKING-CHANGES.md
- `jsonschema` crate docs — https://docs.rs/jsonschema/latest/jsonschema/
- Confluent Schema Registry API — https://docs.confluent.io/platform/current/schema-registry/develop/api.html
- Confluent schema evolution docs — https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
- `schema-registry-compatibility` crate docs — https://docs.rs/schema-registry-compatibility/latest/schema_registry_compatibility/
- Schemars derive docs — https://docs.rs/schemars/latest/schemars/derive.JsonSchema.html
