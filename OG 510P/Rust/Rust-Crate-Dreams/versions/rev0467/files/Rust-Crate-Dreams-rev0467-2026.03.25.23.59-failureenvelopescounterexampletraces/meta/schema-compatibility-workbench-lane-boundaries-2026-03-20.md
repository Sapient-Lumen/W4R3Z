# schema-compatibility-workbench lane boundaries — 2026-03-20

This note keeps **P-0124 Schema Compatibility Workbench Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable compatibility contract** over published schema surfaces.
It should answer:

- what was compared,
- under which compatibility profile,
- with what finding strength,
- and under which policy decision.

## Keep this distinct from nearby lanes

### Distinct from `P-0024 data-contract-kit`

`P-0024` is registry/contract-workflow-first for streaming and eventing systems.
`P-0124` is broader and more review-surface-first across OpenAPI, JSON Schema, Protobuf, and imported registry checks.

### Distinct from `P-0099 schema-evolution-workbench-kit`

`P-0099` is about persisted Serde data, versioned wire/domain types, and migration proofs.
`P-0124` is about published schema compatibility review, not migration graphs over app-owned persisted state.

### Distinct from OpenAPI / JSON Schema toolchains

This lane is not:

- another authoring generator,
- another parser,
- or another validator.

It should import those tools and publish one contract layer above them.

### Distinct from public-API readiness / release-review lanes

Those lanes join semver, docs, cfg availability, dependency boundaries, and review posture.
This lane only covers **machine-readable schema compatibility truth**.

## Four truths this lane must keep separate

1. **comparison basis** — old/new inputs, normalization, history scope, generated-vs-authored basis;
2. **compatibility profile** — engine/profile/category/threshold meaning;
3. **finding strength** — definite, potential, validation-only, witness-backed, or manual-review;
4. **policy decision** — ignores, waivers, fail thresholds, and final gate result.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- latest-only and transitive history checks,
- wire compatibility and generated-source compatibility,
- JSON Schema validation and compatibility proof,
- warning-bearing findings and mechanically definite breaks,
- green gates and waiver-free review results.

## Preferred artifact vocabulary

- `comparison-basis.receipt`
- `compatibility-profile.receipt`
- `finding-strength.report`
- `policy-decision.report`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.
