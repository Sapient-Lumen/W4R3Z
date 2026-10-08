# OpenAPI 3.1 + JSON Schema 2020-12 Toolchain Kit — product plan (2026-03-21)

This note sharpens **P-0224 OpenAPI 3.1 + JSON Schema 2020-12 Toolchain Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0224** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should **not** try to become a universal generator, a final API governance platform, or an omniscient breaking-change oracle.
It should provide one boring, reviewable **OpenAPI 3.1 / JSON Schema toolchain contract** above today's parsers, validators, emitters, and generators.

`0.1` should make five things first-class:

1. **dialect identity** — what Schema Object dialect, meta-schema, and vocabulary posture the tool assumed;
2. **ref-resolution route** — which entry document, base URI, fetch policy, and cache/mirror route produced the resolved graph;
3. **bundle / projection policy** — whether refs were preserved, flattened, rewritten, or narrowed for review/codegen/docs/gateway use;
4. **compatibility profile** — which consumer expectations were checked and which were not;
5. **semantic-diff authority** — whether the diff is descriptive only or coupled to a named policy/verdict layer.

## What `0.1` should provide other people

- one compact `dialect-profile.receipt.json`
- one compact `ref-resolution.receipt.json`
- one compact `bundle-projection.report.json`
- one compact `compatibility-profile.receipt.json`
- one compact `semantic-diff.report.json`
- one compact `oas-bundle.manifest.json`
- one normalized OpenAPI JSON output
- one portable review/support bundle

## Commands worth shipping first

- `cargo oas-contract inspect`
- `cargo oas-contract resolve`
- `cargo oas-contract bundle`
- `cargo oas-contract compat`
- `cargo oas-contract diff`
- `cargo oas-contract explain`

## What to import, not reinvent

- parsing/model substrate from crates such as `openapiv3_1` or `oas3`
- generic JSON Schema validation substrate from `jsonschema`
- code-first emitters such as `utoipa`
- the shared bundle substrate from **P-0256 Evidence Bundle Core Kit**

## Suggested `0.1` doctor warnings

- `openapi_schema_object_dialect_flattened_to_plain_jsonschema`
- `remote_ref_fetch_happened_without_visible_policy`
- `codegen_projection_claimed_as_review_bundle`
- `structurally_valid_but_outside_named_consumer_profile`
- `semantic_diff_claims_breaking_without_policy_basis`
- `3_0_x_input_claimed_as_lossless_3_1_x_contract`

## First proving-ground scenarios

1. **OpenAPI Schema Objects are based on JSON Schema 2020-12, but they still live in the OpenAPI 3.1 dialect and must not be mislabeled as plain draft-2020-12.**
2. **Relative and remote refs are operational facts, so offline-only, mirror-only, and network-allowed resolution need visible receipts.**
3. **A review bundle that preserves refs is not the same artifact as a generator-friendly flattened projection.**
4. **A document can be structurally valid while still missing a downstream consumer profile.**
5. **A semantic diff should describe what changed before any rule pack declares it breaking or non-breaking.**

## What to leave for later

- full generator ecosystems and framework adapters
- hosted governance dashboards
- universal 3.0.x ↔ 3.1.x migration automation
- remote registry/discovery infrastructure
- claims that one compatibility profile covers all tools forever
