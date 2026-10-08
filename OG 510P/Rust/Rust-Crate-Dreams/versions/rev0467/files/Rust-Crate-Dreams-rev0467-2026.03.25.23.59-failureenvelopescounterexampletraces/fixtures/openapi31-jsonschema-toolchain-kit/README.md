# OpenAPI 3.1 + JSON Schema 2020-12 Toolchain Kit fixtures

These fixtures exercise the `0.1` artifact vocabulary for **P-0224 OpenAPI 3.1 + JSON Schema 2020-12 Toolchain Kit**.

## Core schemas

- `dialect-profile.receipt.schema.json`
- `ref-resolution.receipt.schema.json`
- `bundle-projection.report.schema.json`
- `compatibility-profile.receipt.schema.json`
- `semantic-diff.report.schema.json`
- `oas-bundle.manifest.schema.json`

## Scenario families

- `openapi_schema_object_dialect_is_not_plain_draft2020_12/` — keep OpenAPI 3.1 Schema Object dialect identity separate from generic draft-2020-12 folklore.
- `remote_and_relative_refs_require_explicit_resolution_policy/` — keep entry document, base URI, fetch policy, and offline posture explicit.
- `review_bundle_keeps_refs_but_codegen_projection_can_flatten/` — keep review-preserving bundles distinct from generator-friendly flattened projections.
- `consumer_profile_gap_exists_even_when_spec_is_structurally_valid/` — keep structural validity distinct from a named downstream compatibility profile.
- `semantic_diff_must_not_equal_breaking_change_verdict/` — keep descriptive diffs distinct from policy-backed breaking/non-breaking judgments.

The point of this fixture pack is to stop future passes from flattening:

- dialect identity,
- ref-resolution route,
- projection policy,
- compatibility profile,
- and semantic-diff authority

into one fake "OpenAPI 3.1 support" story.
