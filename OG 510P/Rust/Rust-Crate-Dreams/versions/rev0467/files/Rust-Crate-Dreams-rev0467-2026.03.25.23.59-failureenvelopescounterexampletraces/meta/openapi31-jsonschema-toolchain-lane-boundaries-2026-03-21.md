# openapi31-jsonschema-toolchain lane boundaries — 2026-03-21

This note keeps **P-0224 OpenAPI 3.1 + JSON Schema 2020-12 Toolchain Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable toolchain contract** over one OpenAPI 3.1 description, its Schema Object dialect assumptions, its reference-resolution route, its projection policy, its compatibility profile, and its semantic-diff authority.
It should answer:

- what dialect assumptions were used,
- how refs were resolved,
- whether the artifact is review-oriented or projection-oriented,
- which consumer profile was checked,
- and whether any breaking verdict came from a named policy.

## Keep this distinct from nearby lanes

### Distinct from raw parser / model crates

`openapiv3_1`, `oas3`, and similar crates are substrate.
`P-0224` is the support contract above them.

### Distinct from generic JSON Schema validators

`jsonschema` and peers are generic validation substrate.
`P-0224` is the OpenAPI-specific review vocabulary above that substrate.

### Distinct from code-first OpenAPI emitters

`utoipa` and similar crates emit OpenAPI descriptions from Rust code.
`P-0224` is the post-emission / post-ingest review and support lane.

### Distinct from generator-specific SDK/client/server tools

Generator crates and external generators are consumers of OpenAPI descriptions.
`P-0224` is the contract layer that can tell a generator what dialect/resolution/projection/compatibility story it is receiving.

### Distinct from API governance portals or hosted review systems

Dashboards and policy services are downstream consumers.
`P-0224` should stay small enough to work as a local crate + bundle vocabulary.

## Five truths this lane must keep separate

1. **dialect identity** — OpenAPI 3.1 Schema Object dialect vs generic JSON Schema assumptions;
2. **ref-resolution route** — entry document, base URI, fetch policy, and cache/mirror route;
3. **bundle / projection policy** — review-preserving bundle vs flattened/narrowed projection;
4. **compatibility profile** — which consumer profile was checked and what it requires;
5. **semantic-diff authority** — descriptive diff facts vs policy verdict.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- OpenAPI Schema Object dialect and plain draft-2020-12 lore,
- structural validity and compatibility with a named downstream consumer,
- a review bundle and a generator-friendly flattened projection,
- a resolved ref graph and a visible resolution policy,
- descriptive diffs and breaking-change verdicts,
- or 3.0.x tolerance and lossless 3.1.x fidelity.

## Preferred artifact vocabulary

- `dialect-profile.receipt`
- `ref-resolution.receipt`
- `bundle-projection.report`
- `compatibility-profile.receipt`
- `semantic-diff.report`
- `oas-bundle.manifest`

If a future pass adds more detail, extend one of those objects before inventing a vague new umbrella.
