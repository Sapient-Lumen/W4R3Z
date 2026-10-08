# Design: Public SDK family default lane (contract truth + generated code truth + runtime/auth truth + release/support truth)

## Goal
Add the first maintained **public SDK family** defaults-corpus card so the archive can answer a recurring practical question:
**what should a serious Rust API SDK family normalize around right now if the team wants the clearest boring default?**

This lane should not replace the broader `design/sdk-productization-stack.md`.
It should give that stack one bounded maintained answer for a very common project class.

## Why this note is needed now
The archive already has:
- a strong abstract **SDK Productization Stack**;
- a **publishable library** card for reusable public crates;
- and several product/runtime cards for apps, web products, and polyglot boundaries.

But it still lacked a maintained answer for the recurring case where the public Rust artifact is **an SDK family derived from an HTTP/OpenAPI contract** rather than a hand-authored general-purpose crate.

That omission is harder to justify now because:
- Rust’s March 20, 2026 challenges post still frames ecosystem navigation as a problem of **choice paralysis** and **tacit knowledge**;
- the 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated workflows rise;
- `utoipa` now clearly supports a code-first OpenAPI path for Rust-owned HTTP APIs;
- `progenitor` now clearly supports opinionated Rust client generation from OpenAPI 3.0.x documents and can also generate CLI and `httpmock` helpers;
- OpenAPI Generator still maintains a Rust generator with multiple runtime/template options, which keeps the lane honest about serious alternatives;
- `smithy-rs` and the AWS SDK for Rust remain strong proof that generated SDK families are real products with configuration, examples, and maintenance posture rather than just codegen output;
- Oxide’s Rust SDK/CLI repo remains the clearest Rust-native practical blueprint: one OpenAPI source, checked-in generated code, CLI + SDK + mock family, CI sync, and explicit versioning policy;
- Cargo/docs.rs/crates.io now expose enough publication and review surface that public SDKs can be treated as inspectable products instead of generator folklore.

Together those signals say the next worthy move is **not** another generator comparison essay.
It is a bounded boring default card.

## Chosen project class
The first SDK-family card should cover:
- public Rust SDK crates for HTTP/JSON APIs where an OpenAPI description is already part of the product truth;
- teams that want one source contract, one Rust SDK crate family, checked examples, and a release/review path that survives regeneration;
- APIs where generated code is expected, but hand-written overlays, helpers, or companion CLI/mock artifacts are still legitimate;
- products where auth/config/runtime truth, versioning truth, docs truth, and exact package identity matter alongside the generated surface.

It should **not** try to cover in one card:
- gRPC/protobuf-first APIs where `tonic-build` or descriptor-driven flows are the true center;
- Smithy-first multi-service SDK families where Smithy models and smithy-runtime assumptions dominate;
- internal one-off generated clients with no public semver/support story;
- or generic reusable crates that just happen to talk HTTP.

## Default thesis
For this bounded project class, the conservative default should currently be:

**checked-in OpenAPI contract + `progenitor`-generated async SDK client + thin hand-written overlay/helpers + checked examples/docs + explicit semver/release discipline**.

Why this is the right first card:
- `progenitor` is Rust-native and opinionated instead of hiding Rust shape behind a giant multi-language generator surface.
- It already spans more than “just the client” by supporting CLI and `httpmock` helper generation, which matches the real SDK-family shape.
- Oxide demonstrates that checked-in generated code plus CI sync is not theoretical; it is already a practical Rust-native pattern.
- The lane stays honest about generated-versus-hand-written ownership instead of pretending the output is either sacred or irrelevant.
- The lane stays honest about runtime/config/auth and release/docs truth instead of pretending the OpenAPI file alone is the whole product.

## Serious alternatives that must stay visible
### 1. OpenAPI Generator Rust lane
This wins when the same upstream OpenAPI contract must feed many languages, when the team needs its broader runtime/template matrix, or when `reqwest-trait` / middleware / generator-template customization matters more than a Rust-native opinionated path.

### 2. Smithy / smithy-rs lane
This wins when the real product is a large multi-service SDK family, when Smithy is the authoritative contract language, or when lower-level runtime/config control and service-per-crate structure are central.

### 3. gRPC / protobuf lane with `tonic-build`
This wins when protobuf descriptors are the contract source of truth and generated gRPC service/client code is the actual family center rather than HTTP/OpenAPI.

## What the card must keep separate
The maintained card should visibly preserve:
- **source-contract truth**;
- **generated-code truth**;
- **hand-written overlay truth**;
- **runtime/auth/config truth**;
- **docs/example/mock/CLI family truth**;
- **release/versioning/package-identity truth**;
- **support/docs truth**;
- and **lane judgment** versus project-specific escalation.

## Non-goals
- declaring one universal SDK generator for Rust;
- pretending all Rust SDKs are OpenAPI-shaped;
- pretending generated code alone is the whole support story;
- or turning the defaults corpus into an API-generator benchmark scoreboard.

## Archive implications
- Add a first maintained public-SDK-family card under `defaults/`.
- Add a first renewal receipt under `evidence/`.
- Refresh corpus/frontier/meta files so the repo treats **public SDK family** as a maintained lane distinct from both **publishable library** and **polyglot workspace component**.
- Keep future narrower cards available, especially a separate **Smithy/official large-SDK family** card or a **gRPC/protobuf public SDK** card if the evidence warrants them later.

## References
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `utoipa`:
  https://docs.rs/utoipa
- `progenitor`:
  https://docs.rs/progenitor
  https://github.com/oxidecomputer/progenitor
- OpenAPI Generator Rust:
  https://openapi-generator.tech/docs/generators/rust/
- `tonic` / `tonic-build`:
  https://docs.rs/tonic
  https://docs.rs/tonic-build
- `smithy-rs` and Smithy Rust design docs:
  https://github.com/smithy-lang/smithy-rs
  https://smithy-lang.github.io/smithy-rs/design/
- AWS SDK for Rust:
  https://docs.aws.amazon.com/sdk-for-rust/latest/dg/welcome.html
- Oxide SDK and CLI:
  https://github.com/oxidecomputer/oxide.rs
- Cargo semver and publishing:
  https://doc.rust-lang.org/cargo/reference/semver.html
  https://doc.rust-lang.org/cargo/reference/publishing.html
- docs.rs builds and `cargo docs-rs`:
  https://docs.rs/about/builds
  https://docs.rs/crate/cargo-docs-rs/latest
- crates.io review surfaces and Trusted Publishing:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://crates.io/docs/trusted-publishing
- public/private dependencies goal:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
