---
id: P-0124
title: Schema Compatibility Workbench Kit (OpenAPI + JSON Schema + Protobuf)
status: idea
domains: [api, schemas, devtools, compatibility, standards]
last_reviewed: 2026-03-20
evidence:
  - https://buf.build/docs/breaking/
  - https://github.com/oasdiff/oasdiff/blob/main/docs/BREAKING-CHANGES.md
  - https://docs.rs/jsonschema/latest/jsonschema/
  - https://docs.confluent.io/platform/current/schema-registry/develop/api.html
  - https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
  - https://docs.rs/schemars/latest/schemars/derive.JsonSchema.html
  - https://docs.rs/schema-registry-compatibility/latest/schema_registry_compatibility/
---

# Problem

Rust teams increasingly publish **machine-readable schemas** as public contracts:

- OpenAPI for service boundaries,
- JSON Schema for API payloads and config files,
- Protobuf for RPC and streaming,
- and registry-managed subjects for event-driven systems.

The substrate is much better than it used to be:

- **Buf** already gives serious Protobuf breaking-change detection with configurable rule categories.
- **oasdiff** already detects OpenAPI changes and classifies them by severity.
- Rust’s **jsonschema** crate already gives fast standards-aware validation with structured reports.
- **Confluent Schema Registry** already exposes compatibility modes, normalization, verbose failure output, and latest-vs-transitive subject checks.
- **Schemars** already derives JSON Schema from Rust types while respecting many Serde attributes.

But downstream users still usually cannot answer four boring questions from one artifact:

1. **What exact old/new surfaces were compared?**
2. **Which compatibility profile was actually applied?**
3. **How strong is each finding — definite, potential, witness-backed, or validation-only?**
4. **Which exceptions, ignored rules, or gate thresholds changed the final decision?**

That means teams still over-read claims like:

- “schema-compatible”,
- “no breaking changes”,
- “passes Buf”,
- “OpenAPI diff is clean”,
- “registry check passed”,
- or “JSON Schema validation succeeded”.

Those claims can all be technically true while still hiding whether the check was:

- latest-only instead of transitive,
- wire-only instead of generated-source sensitive,
- normalized or non-normalized,
- warning-bearing instead of mechanically definite,
- or green only because specific findings were ignored.

The missing crate is **not** another schema authoring toolkit, **not** another registry server, and **not** another wrapper pretending all formats share one semantics.

The missing crate is a **reviewable schema-compatibility contract layer** above today’s engines.

# Main judgment

A worthwhile `0.1` should not try to unify all schema evolution semantics into one fake global truth.
It should instead publish four compact review objects:

1. **comparison-basis truth** — what was compared, from where, with which normalization and history scope;
2. **compatibility-profile truth** — which engine/profile/rule family defined “compatible” for this run;
3. **finding-strength truth** — whether a finding is mechanically definite, potential, witness-backed, validation-only, or still manual-review-only;
4. **policy-decision truth** — what ignore lists, waivers, thresholds, or review decisions produced the final gate result.

# Why this lane got stronger

## 1. Buf made Protobuf compatibility a serious, configurable review surface

Buf’s breaking docs now present compatibility checking as a formal part of development, code review, and registry enforcement.
Its categories (`FILE`, `PACKAGE`, `WIRE_JSON`, `WIRE`) prove that “compatibility” is profile-dependent even within one engine.

## 2. oasdiff already has severity classes and ignore files

oasdiff is explicit that some checks are definite breaking changes (`ERR`), some are only potential (`WARN`), and some are informational.
It also allows ignore files and fail thresholds.
That means a green OpenAPI gate can hide real policy nuance.

## 3. Rust’s JSON Schema substrate is strong at validation, not universal compatibility semantics

The `jsonschema` crate supports multiple drafts and structured validation output.
That makes it powerful substrate, but it does not itself answer the broader review question “is this schema evolution compatible for this audience and policy?”

## 4. Registry-backed compatibility is scoped by subject configuration and history mode

Confluent’s API and docs are explicit that compatibility checks depend on the subject/global compatibility level, whether checks are transitive or latest-only, whether normalization is enabled, and whether verbose reasons are requested.
So “registry compatibility passed” is not one invariant thing.

## 5. Generated schemas are already influenced by Rust-side serialization meaning

Schemars says derived schemas should describe the JSON representation produced by `serde_json` and generally respect Serde attributes.
That means the generation basis itself matters: a check over generated schemas is partly a check over the Rust-side serialization contract.

# What it should provide other people

## 1) `comparison-basis.receipt.json`

This artifact should answer:

- which schema family is in play,
- what old and new inputs were compared,
- whether inputs were file snapshots, generated artifacts, registry subjects, git refs, or imported engine outputs,
- whether normalization happened,
- whether history scope was pairwise latest, transitive/all-history, or unknown,
- and whether the basis is direct, imported, or mixed.

## 2) `compatibility-profile.receipt.json`

This artifact should answer:

- which engine or rule family produced the result,
- which profile vocabulary was used,
- which threshold/gate level applied,
- and whether the run is client-facing, server-facing, wire-facing, registry-policy-facing, or manual-review-only.

Examples:

- Buf `FILE` vs `WIRE`
- OpenAPI `ERR`/`WARN` threshold
- registry `BACKWARD` vs `FULL_TRANSITIVE`
- local pairwise diff versus subject-history check

## 3) `finding-strength.report.json`

This artifact should answer:

- which findings were observed,
- whether each is `definite_breaking`, `potential_breaking`, `validation_only`, `witness_backed`, `manual_review_required`, or `not_evaluated`,
- whether a concrete witness/example exists,
- and which parts of the claim rely on imported engine meaning rather than native proof.

## 4) `policy-decision.report.json`

This artifact should answer:

- which rules/findings were ignored,
- which waivers or issue links were attached,
- what fail threshold was used,
- whether the final result is `pass`, `pass_with_exceptions`, `review_required`, or `fail`,
- and what still needs manual review.

## 5) A cargo-native UX

The crate should provide a UX such as:

- `cargo schema-contract capture`
- `cargo schema-contract check`
- `cargo schema-contract diff`
- `cargo schema-contract gate`
- `cargo schema-contract bundle`

This should emit one reviewable `.schemacontractbundle.zip`.

# Distinctive implementation shape

## Crates

- `schema_contract_model` — artifact types, validators, rendering
- `schema_contract_import_openapi` — oasdiff import/normalization
- `schema_contract_import_proto` — Buf import/normalization
- `schema_contract_import_registry` — subject-history / compatibility-mode capture
- `schema_contract_import_jsonschema` — JSON Schema validation + draft/context capture
- `schema_contract_check` — coherence and policy checks
- `schema_contract_pack` — bundle packing/diffing
- `cargo-schema-contract` — CLI

## One important design rule

**Do not flatten engine meaning.**

The crate should normalize artifact shape, not pretend that:

- OpenAPI request/response compatibility,
- Protobuf generated-source compatibility,
- wire compatibility,
- JSON instance validation,
- and registry subject-policy checks

are the same thing.

# Recommended `0.1` command surface

## `cargo schema-contract capture`
Capture imported/native facts and emit:

- `comparison-basis.receipt.json`
- `compatibility-profile.receipt.json`
- `finding-strength.report.json`
- `policy-decision.report.json`

## `cargo schema-contract check`
Run coherence checks such as:

- latest-only result over-read as transitive
- validation pass presented as compatibility proof
- warning-level findings suppressed without visible disclosure
- wire-compat result over-read as generated-source compatibility

## `cargo schema-contract diff`
Compare two contract bundles and classify:

- `basis_changed`
- `profile_changed`
- `finding_strength_changed`
- `waiver_added`
- `threshold_changed`
- `manual_review_boundary_changed`

## `cargo schema-contract bundle`
Produce one compact `.schemacontractbundle.zip` suitable for CI artifacts and release review.

# Preferred proving grounds

- a Rust service generating OpenAPI and gating it in CI,
- a Protobuf workspace already using Buf,
- an eventing project using registry-backed compatibility modes,
- a config/API crate deriving JSON Schema from Rust types,
- a mixed system that publishes more than one schema family and needs one joined review surface.

# Non-goals

- not a replacement for Buf,
- not a replacement for oasdiff,
- not a full schema registry,
- not a universal proof that semantic behavior stayed the same,
- not another OpenAPI/JSON Schema/Protobuf authoring toolkit,
- not a claim that every schema family can share one “breaking change” semantics.

# Adoption path

1. Start with **import-first** adapters over existing engines.
2. Stabilize the contract artifacts before adding too much engine-specific cleverness.
3. Make CI summaries and PR comments read from the contract bundle.
4. Let adjacent crates consume the same bundle for upgrade reviews, support docs, or platform governance.

# Why this would count as a worthy crate contribution

A worthy contribution here would make one especially ordinary review problem boring:

- another team could stop asking “what exactly did this green schema check mean?”
- and start reading one compact bundle that says **what was compared, under which rules, with what strength, and with which exceptions**.

That is a substrate-level improvement for API teams, platform teams, registry users, service owners, and maintainers — and it composes with the rest of the Rust ecosystem instead of competing with it.
