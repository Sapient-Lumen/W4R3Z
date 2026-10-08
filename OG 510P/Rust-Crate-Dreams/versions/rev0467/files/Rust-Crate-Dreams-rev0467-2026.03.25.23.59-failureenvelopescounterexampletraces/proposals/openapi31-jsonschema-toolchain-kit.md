---
id: P-0224
title: OpenAPI 3.1 + JSON Schema 2020-12 Toolchain Kit — dialect-aware bundle / resolve / compare / review support
status: idea
domains: [api, openapi, json-schema, tooling, codegen, interop, conformance]
last_reviewed: 2026-03-21
evidence:
  - https://spec.openapis.org/oas/v3.1.0
  - https://spec.openapis.org/oas/3.1/dialect/2024-11-10.html
  - https://json-schema.org/draft/2020-12
  - https://docs.rs/openapiv3_1/latest/openapiv3_1/
  - https://docs.rs/oas3/latest/oas3/
  - https://docs.rs/jsonschema/latest/jsonschema/
  - https://docs.rs/crate/utoipa/latest
needs:
  - A default Rust support layer for OpenAPI 3.1 that treats OpenAPI Schema Objects as their own JSON Schema 2020-12-based dialect instead of flattening them into "plain draft 2020-12" folklore.
  - A boring way to turn parsing, reference resolution, bundling, compatibility review, and semantic diff claims into portable review artifacts instead of tool-specific screenshots and one-off scripts.
  - A way to keep structural validity, consumer compatibility, and semantic-diff policy separate even when a spec is syntactically valid.
risks:
  - Scope creep: this lane can easily sprawl into a whole generator ecosystem, a framework-specific derive story, or a hosted API governance product.
  - False authority: a crate can over-claim "breaking change" or "fully valid" even though consumer profiles, dialect handling, and reference policy remain partial.
  - Interop drag: OpenAPI 3.0.x, code-first emitters, and generator-specific expectations still matter, so downgrade/upgrade boundaries need to stay explicit.
---

## Problem
Rust now has credible OpenAPI 3.1 and JSON Schema building blocks, but it still lacks one compact **toolchain contract** for the questions downstream teams actually fight about in review:

- **Which dialect is this schema surface actually using?**
- **How were relative or remote references resolved, and under what offline/network policy?**
- **Is this artifact a review bundle that preserves structure, or a projection optimized for codegen?**
- **Is the document only structurally valid, or does it also fit a stated consumer/generator profile?**
- **Does a semantic diff describe changes only, or does it also claim a policy verdict such as breaking / non-breaking?**

Today those truths are scattered across parser crates, validator crates, code-first emitters, and generator tools.
That means teams can still end up with "valid in tool A, broken in tool B" arguments that are hard to reproduce and harder to review.

## Main judgment
A worthy crate here should **not** try to become the OpenAPI spec, a universal SDK generator, or a web framework.
It should provide one boring, reviewable support layer above today's parsers and validators.

The first implementation should make five review objects first-class:

1. **dialect identity** — what OpenAPI/JSON Schema dialects and vocabularies were assumed;
2. **ref-resolution route** — which entry documents, base URIs, caches, fetches, and offline rules produced the resolved graph;
3. **bundle / projection policy** — whether refs were preserved, rewritten, flattened, inlined, redacted, or narrowed for another consumer;
4. **compatibility profile** — which downstream consumer expectations were checked (review profile, docs renderer profile, generator profile, gateway profile, etc.);
5. **semantic-diff authority** — whether a diff is descriptive only or also tied to an explicit policy/verdict layer.

## What this crate should provide other people

Version `0.1` should give downstream users small, portable artifacts instead of one giant magic command:

- one `dialect-profile.receipt.json`
- one `ref-resolution.receipt.json`
- one `bundle-projection.report.json`
- one `compatibility-profile.receipt.json`
- one `semantic-diff.report.json`
- one `oas-bundle.manifest.json`
- one optional normalized OpenAPI JSON document
- one optional review bundle ZIP for support / CI / PR discussion

Those artifacts should let somebody else answer:

- what the entry document was,
- which refs were fetched or refused,
- which dialect rules mattered,
- whether flattening/inlining happened,
- what consumer profile was checked,
- and whether a semantic diff is merely descriptive or was judged under policy.

## Users
- API platform teams reviewing contract changes in CI.
- SDK / gateway / docs-generator maintainers who need explicit resolution and compatibility posture.
- code-first API authors who emit OpenAPI 3.1 but still need an external review/bundling/checking pipeline.
- support / incident teams trying to reproduce "tool A accepted this, tool B rejected it" cases.

## Prior art and why it is not enough
- **OpenAPI 3.1 spec + dialect docs** define the ground truth, but they are not a review bundle or CI support contract.
- **`openapiv3_1`** gives Rust structures for OpenAPI 3.1 and notes full JSON Schema 2020-12 definitions, but it is not itself the whole review/resolution/compatibility pipeline.
- **`oas3`** parses, navigates, and validates OpenAPI 3.1.x, but does not by itself define portable review receipts for dialect, resolution route, projection policy, or diff authority.
- **`jsonschema`** is strong validator substrate with reusable validators and external-ref support, but it is generic JSON Schema infrastructure rather than OpenAPI-specific review vocabulary.
- **`utoipa`** is strong code-first generation substrate, but code-first emission is not the same thing as a portable post-emission contract checker.

## Design goals
- **Dialect fidelity first.** Do not silently collapse OpenAPI Schema Objects into generic draft-2020-12 folklore.
- **Reproducible ref handling.** Networked resolution, offline mirrors, and refusal-to-fetch should each be visible.
- **Projection honesty.** Review bundles, codegen-friendly projections, and docs-renderer projections should not be conflated.
- **Compatibility without mysticism.** A crate may say "structurally valid but outside profile X".
- **Diff modesty.** A semantic diff should be descriptive first; any breaking/non-breaking verdict must cite an explicit profile or rule pack.
- **Evidence portability.** Review/support artifacts should be small enough to attach to PRs, incidents, or CI logs.

## Non-goals
- Becoming the final OpenAPI server/client framework.
- Replacing every code-first emitter or generator.
- Claiming universal breaking-change truth across all consumers.
- Fetching arbitrary network refs by default without visible policy.

## Suggested workspace shape
- `oas-contract-core` — manifest types, normalized OpenAPI document form, stable JSON writer.
- `oas-contract-dialect` — dialect identification, vocabulary receipts, Schema Object posture.
- `oas-contract-refs` — ref graph walk, base-URI policy, offline/network resolution receipts.
- `oas-contract-bundle` — review bundle assembly, projection reports, redaction/narrowing notes.
- `oas-contract-compat` — consumer profiles and explainable compatibility checks.
- `oas-contract-diff` — semantic-diff IR plus explicit rule-pack / policy attachment.
- `cargo-oas-contract` — CLI glue (`inspect`, `resolve`, `bundle`, `compat`, `diff`).

## Version `0.1` MVP
1. Parse YAML/JSON OpenAPI 3.1 documents into a stable normalized representation.
2. Emit `dialect-profile.receipt.json` and `ref-resolution.receipt.json`.
3. Support explicit resolution modes: `offline-only`, `mirror-only`, `network-allowed`, `embedded-only`.
4. Emit `bundle-projection.report.json` for review bundle vs codegen projection.
5. Emit `compatibility-profile.receipt.json` for a few curated profiles.
6. Emit `semantic-diff.report.json` that keeps descriptive change facts separate from verdict policy.
7. Package everything into `oas-bundle.manifest.json` + optional zip support bundle.

## De-risk plan
- Start with a narrow OpenAPI 3.1-only contract instead of promising full 3.0.x / 3.1.x round-tripping.
- Keep compatibility profiles versioned and explicit.
- Keep remote fetching opt-in and receipt-backed.
- Treat codegen as an optional projection consumer, not the authority for normalization.

## What success looks like
A team should be able to attach one small bundle to a PR or support issue and answer:

- which OpenAPI/JSON Schema dialect assumptions were used,
- which refs were followed or refused,
- which projection was produced,
- which compatibility profile was checked,
- and whether any breaking verdict came from a named policy instead of hand-waving.

## Sources
- OpenAPI 3.1 specification: https://spec.openapis.org/oas/v3.1.0
- OpenAPI 3.1 Schema Object dialect: https://spec.openapis.org/oas/3.1/dialect/2024-11-10.html
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- `openapiv3_1`: https://docs.rs/openapiv3_1/latest/openapiv3_1/
- `oas3`: https://docs.rs/oas3/latest/oas3/
- `jsonschema`: https://docs.rs/jsonschema/latest/jsonschema/
- `utoipa`: https://docs.rs/crate/utoipa/latest
