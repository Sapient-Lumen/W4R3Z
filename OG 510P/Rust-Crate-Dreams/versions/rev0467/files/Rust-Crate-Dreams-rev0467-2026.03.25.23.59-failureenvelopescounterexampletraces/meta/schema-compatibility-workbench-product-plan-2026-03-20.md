# schema-compatibility-workbench-kit product plan — 2026-03-20

This note sharpens **P-0124 Schema Compatibility Workbench Kit** into an implementation-ready `0.1` direction.

## Main judgment

A worthwhile `0.1` should **not** try to become:

- another OpenAPI diff engine,
- another Protobuf breaking checker,
- another schema registry,
- or a universal theorem prover for semantic compatibility.

It should instead become a **reviewable contract layer** that helps a project publish one boring, inspectable answer to four high-value questions:

1. **What exact schema surfaces were compared?**
2. **Which compatibility profile defined “compatible”?**
3. **How strong is each finding?**
4. **Which policy choices produced the final gate result?**

The missing value is the contract layer above today’s engines and registries.

## Why this lane got stronger

Current schema substrate makes the gap more actionable than it used to be:

- Buf treats compatibility as a configurable check with distinct categories and review phases.
- oasdiff has explicit severity classes and ignore mechanics.
- `jsonschema` is strong at standards-aware validation but does not itself settle review-level compatibility semantics.
- Confluent Schema Registry makes compatibility mode, transitivity, normalization, and verbose reasoning part of the effective result.
- Schemars ties generated schemas to Rust-side serialization meaning.
- `schema-registry-compatibility` proves there is already native Rust compatibility substrate worth importing.

That means the ecosystem no longer mainly lacks raw primitives.
It lacks a **shared product-shape** for publishing schema compatibility truth.

## What the crate should provide other people

For API teams, platform engineers, release reviewers, registry users, and downstream adopters, the crate should provide:

1. **One comparison-basis receipt** instead of hand-wavy “compared v1 to v2”.
2. **One compatibility-profile receipt** instead of implicit engine defaults.
3. **One finding-strength report** instead of flattening warnings, hard breaks, validation failures, and imported engine judgments.
4. **One policy-decision report** instead of green CI hiding ignore files and waivers.
5. **One compact contract-check report** that keeps imported facts, observed findings, and manual-review zones visibly separate.

## Four first-class review objects

### 1. `comparison-basis.receipt`

This artifact should answer:

- which schema family is being described,
- what old and new inputs were used,
- whether the inputs were generated, checked-in, registry-managed, or imported,
- whether normalization was applied,
- whether the history scope is pairwise/latest-only, transitive/all-history, or mixed,
- and whether the basis is direct or imported.

### 2. `compatibility-profile.receipt`

This artifact should answer:

- which engine/profile family is in play,
- whether the result is client-facing, server-facing, wire-facing, registry-policy-facing, or validation-only,
- which category or severity threshold applied,
- and whether rule-selection or engine defaults materially shaped the result.

### 3. `finding-strength.report`

This artifact should answer:

- which findings were observed,
- how each finding should be read (`definite_breaking`, `potential_breaking`, `validation_only`, `witness_backed`, `not_evaluated`, `manual_review_required`),
- whether a concrete witness exists,
- and what still relies on imported engine meaning.

### 4. `policy-decision.report`

This artifact should answer:

- which rules/findings were ignored,
- which waivers or issue refs exist,
- what fail threshold or review mode was applied,
- and whether the outcome is `pass`, `pass_with_exceptions`, `review_required`, or `fail`.

## Recommended `0.1` command surface

### `cargo schema-contract capture`
Capture the declared/imported contract and emit:
- `comparison-basis.receipt.json`
- `compatibility-profile.receipt.json`
- `finding-strength.report.json`
- `policy-decision.report.json`

### `cargo schema-contract check`
Run conservative checks and emit:
- `schema-contract-check.report.json`

### `cargo schema-contract diff`
Compare two bundles and emit:
- `schema-contract-diff.report.json`

### `cargo schema-contract bundle`
Produce one compact `.schemacontractbundle.zip`.

## Recommended crate/workspace split

- `schema_contract_model`
- `schema_contract_import_openapi`
- `schema_contract_import_proto`
- `schema_contract_import_registry`
- `schema_contract_import_jsonschema`
- `schema_contract_check`
- `schema_contract_pack`
- `cargo-schema-contract`

## Discovery order

1. **Surface import**
   - checked-in OpenAPI / JSON Schema / `.proto`
   - generated schema artifacts
   - registry subject/version capture
   - imported engine output
2. **Basis capture**
   - old/new identity
   - normalization
   - history scope
   - generated-vs-authored basis
3. **Profile capture**
   - Buf category
   - OpenAPI severity / fail threshold
   - registry compatibility mode
   - validation-only routes
4. **Finding capture**
   - normalized findings
   - witness availability
   - imported rule identifiers
5. **Policy capture**
   - ignores
   - waivers
   - threshold
   - manual review
6. **Bundle and diff**
   - export one compact review bundle

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- Buf breaking categories and inputs
- oasdiff severity classes and ignore/fail config
- JSON Schema draft/validator context
- registry compatibility modes and transitivity
- generated-schema basis from Schemars or similar tools

### Do not flatten into one fake verdict
- “passes Buf”
- “OpenAPI diff is clean”
- “JSON Schema validates”
- “registry compatibility passed”
- “schema-compatible”

Those are ingredients, not the contract.

## Preferred proving grounds

- a Protobuf workspace already using Buf,
- a service shipping OpenAPI diffs in CI,
- a Rust crate deriving JSON Schema from types,
- an eventing platform using registry-backed compatibility,
- a mixed project needing one shared review summary across schema families.

## Non-goals

- not an engine replacement,
- not a registry replacement,
- not a semantic behavior proof system,
- not a universal compatibility semantics layer,
- not a full authoring toolkit.
