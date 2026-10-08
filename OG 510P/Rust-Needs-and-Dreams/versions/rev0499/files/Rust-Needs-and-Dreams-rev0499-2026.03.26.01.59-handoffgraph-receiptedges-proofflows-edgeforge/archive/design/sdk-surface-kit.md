# Design: SDK Surface Kit (`cargo sdkcheck`, `sdk-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust SDK product surface: package-family identity, operation mapping, config/auth/runtime posture, examples, generated-versus-hand-written ownership, and evidence that the supported SDK still matches its upstream service/schema/protocol inputs.

This should **not** replace `utoipa`, `progenitor`, OpenAPI Generator, `tonic-build`, `smithy-rs`, `reqwest`, or `hyper`.
It should make them easier to combine coherently and easier to ship as a product.

## References (signals)
- The 2024 State of Rust survey says Rust is especially popular for server backends, web/networking services, and cloud technologies.
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- The 2025 State of Rust survey says online documentation remains the canonical reference, hints that some questions are moving to LLM tooling, and notes agentic editors are rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `utoipa` provides code-first OpenAPI generation for Rust REST APIs.
  https://docs.rs/utoipa
- `progenitor` generates opinionated Rust clients from OpenAPI documents.
  https://docs.rs/progenitor
- OpenAPI Generator supports a Rust client lane with multiple HTTP-library templates and middleware/configuration options.
  https://openapi-generator.tech/docs/generators/rust/
- `tonic` explicitly positions codegen as the normal way to use its gRPC client/server surface.
  https://docs.rs/tonic
  https://docs.rs/tonic-build
- `smithy-rs` generates clients, servers, and the AWS SDK for Rust, while also explicitly saying its interfaces are unstable.
  https://github.com/smithy-lang/smithy-rs
- The Smithy Rust design docs show that real SDK users need both a high-level fluent API and lower-level control over transport/dispatch.
  https://smithy-lang.github.io/smithy-rs/design/
- The AWS SDK for Rust documentation includes getting-started, configuration, examples, and maintenance/support references, which is exactly the kind of product surface that goes beyond generated types.
  https://docs.aws.amazon.com/sdk-for-rust/latest/dg/welcome.html
- Oxide’s Rust SDK/CLI repo demonstrates one real Rust API-product workflow where CLI + SDK + mocking library all derive from one OpenAPI source, generated code is checked in, and CI verifies sync.
  https://github.com/oxidecomputer/oxide.rs

## Core components

### 1) `sdk-surface/v0`
A design-time declaration of the SDK family a project intends to ship.

Required ideas:
- SDK family identity (`crate`, workspace, API family, tenant/product flavor)
- package members in scope:
  - core crate
  - transport/runtime crate
  - CLI companion
  - mock/test companion
  - generated-only crate
  - hand-written extension crate
- source contract attachments in scope:
  - OpenAPI
  - Smithy
  - protobuf / descriptor set
  - service-surface / protocol-surface / schema-pack references
- product lanes:
  - `high-level`
  - `low-level`
  - `async`
  - `blocking`
  - `streaming`
  - `cli`
  - `mocking`
- support classes:
  - `official`, `best-effort`, `experimental`, `deprecated`, `internal`

This is the thing humans review before trusting automation.

### 2) `sdk-operation-map/v0`
A portable map from SDK operations to upstream contract identities.

Required ideas:
- stable SDK method/command identifiers
- linked service/protocol/schema operation ids
- request/response/body/streaming posture
- pagination / retry / idempotency hints
- high-level versus low-level operation lanes
- linked auth/config requirement ids
- support level per operation
- deprecated / replacement relationships

Design rule: preserve SDK operation identity even when it was generated from a richer source contract.

### 3) `sdk-runtime-profile/v0`
A machine-readable description of how the SDK behaves operationally.

Required ideas:
- endpoint/base-URL selection posture
- region/tenant/environment selection where relevant
- timeout / retry / backoff posture
- transport stack assumptions
- proxy / TLS / CA / root / user-agent posture
- middleware or interceptor hooks
- credential-source posture by runtime profile
- feature-flag or optional-capability posture

This is the layer ordinary codegen usually leaves scattered across builders, README snippets, and examples.

### 4) `sdk-auth-profile/v0`
A machine-readable description of public authentication and authorization hooks.

Required ideas:
- auth modes in scope (`api-key`, `oauth2`, `bearer`, `sigv4`, cookie/session, custom)
- credential providers and sources
- operation-level auth requirements
- token refresh / signer / session behavior posture
- redaction / secret-handling notes
- linked identity/runtime-setting artifacts where relevant

Design rule: do **not** flatten auth surface into the generic runtime profile; keep it separately reviewable.

### 5) `sdk-example-catalog/v0`
Canonical examples and supportable usage flows.

Potential contents:
- happy-path request examples
- pagination or streaming examples
- auth/config examples
- CLI command examples
- mock/test examples
- migration examples
- provenance labels:
  - illustrative only
  - checked in CI
  - generated from contract
  - validated against fixture server / mock / live sandbox

Design rule: examples should stay small, supportable, and clearly labeled. They are not a traffic dump.

### 6) `sdk-check-plan/v0`
A concrete declaration of what is checked.

Required ideas:
- contract source(s) and generator source(s)
- generated-versus-hand-written boundaries
- selected runtime/auth profiles
- checked crates/CLI/mock members
- checks performed:
  - operation-map extraction
  - source-contract alignment
  - generated-output drift
  - example validation
  - auth/config/retry/profile validation
  - docs/rustdoc/support checks
- unsupported or intentionally omitted lanes

This is where the kit stops pretending “we generate a client” means “we know what we support.”

### 7) `sdk-check-report/v0`
Evidence from code generation, docs, examples, and runtime/profile validation.

Possible contents:
- source-contract summary
- SDK surface summary
- generated drift findings
- auth/profile mismatch findings
- example validation pass/fail
- CLI/SDK/mock family consistency findings
- support/docs mismatch findings
- linked raw artifacts: source spec/model, generated files, checked transcripts, fixture-server logs, and rustdoc/docs builds

### 8) `sdk-diff-report/v0` (optional)
For compatibility-sensitive releases:
- operation added/removed/renamed
- parameter or shape changed
- retry/auth/config posture changed
- support level changed
- CLI command changed
- generated/runtime boundary changed
- documentation-only drift

Should distinguish:
- additive changes
- breaking changes
- generation-only changes
- support-policy changes
- manual follow-up required

### 9) `sdk-pack/v0`
Bundle format containing:
- `sdk-surface/v0`
- `sdk-operation-map/v0`
- `sdk-runtime-profile/v0`
- `sdk-auth-profile/v0`
- optional `sdk-example-catalog/v0`
- one or more `sdk-check-report/v0`
- optional `sdk-diff-report/v0`
- optional raw attachments: OpenAPI specs, Smithy models, descriptor sets, generated-code manifests, checked example transcripts, and rustdoc/support artifacts

This is the unit that should travel through CI, release review, docs publishing, support, and later archaeology.

### 10) `cargo sdkcheck`
Reference UX:
- `cargo sdkcheck init`
- `cargo sdkcheck surface`
- `cargo sdkcheck profiles`
- `cargo sdkcheck examples`
- `cargo sdkcheck diff`
- `cargo sdkcheck pack`

`cargo sdkcheck` should begin as an explainer / adapter / packer.
It should not pretend to be the one true generator, API platform, or auth framework.

## Default policy
- **Separate SDK identity from source-contract identity, runtime profile, auth profile, and support/docs truth.**
- **Preserve source-contract truth and generated-output truth as attachments rather than flattening them into one invented model.**
- **Record generated-versus-hand-written boundaries explicitly** whenever users rely on both.
- **Treat config/auth/retry/streaming posture as part of the product surface**, not as incidental builder code.
- **Distinguish checked examples from illustrative examples** so docs stay honest.
- **Prefer v0 support for OpenAPI, Smithy, and protobuf/gRPC imports** rather than claiming one universal contract language.

## What the kit should provide to others
- **Schema Contract Kit:** link contract surfaces and compatibility reports to stable SDK product identities.
- **Service / Protocol Surface Kits:** attach operation ids and transport/wire assumptions without making the SDK the source of truth for the service.
- **Identity Productization / Credentials / Runtime Settings:** attach auth, signer, secret, and environment activation facts without absorbing them.
- **Library Productization Stack:** import SDK-specific evidence when a Rust crate is actually a platform-facing SDK product rather than an ordinary library.
- **Release Truth / Distribution Contract:** attach SDK packs to published crates, binaries, installers, and release review.
- **Support Envelope / DocProof:** verify rustdoc, examples, target/runtime assumptions, and support claims.

## Overlap boundaries
- **Not another client generator:** code generation remains with `progenitor`, OpenAPI Generator, `tonic-build`, `smithy-rs`, and similar tools.
- **Not another HTTP or RPC runtime:** transport/runtime ergonomics remain with `reqwest`, `hyper`, `tower`, `tonic`, and peers.
- **Not Schema Contract Kit:** upstream schema/protocol truth remains separate; this kit models the derived SDK product surface.
- **Not Identity Productization Stack:** auth/credential truth attaches here by reference but remains separate.
- **Not Library Productization Stack:** generic crate-as-product truth remains broader; SDK Surface is the API-product-specific lane above service/schema contracts.

## Hard problems (explicitly scoped)
1. **Generated and hand-written code coexist for good reasons**
   - v0 should preserve ownership boundaries instead of pretending every SDK is pure generation or pure manual code.
2. **Different source contracts are not identical**
   - OpenAPI, Smithy, and protobuf/gRPC should remain distinct attachments.
3. **SDK compatibility is not only protocol compatibility**
   - generation changes, config/auth changes, and CLI changes can matter even when the wire contract is stable.
4. **Support truth is part of the SDK**
   - examples, rustdoc, auth setup, and maintenance policy are product facts, not afterthoughts.
5. **Release identity matters**
   - many SDK families ship crates, binaries, and mock/test helpers together; v0 must model that family relation honestly.
