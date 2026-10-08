# Default card: Conservative public SDK family (2026 Q1)

Latest renewal receipt: `evidence/conservative-public-sdk-family-2026Q1-renewal-2026-03-22.md`

## Scope
This card applies to:
- public Rust SDK crates for HTTP/JSON APIs where an OpenAPI document is already part of the product truth;
- SDK families where generated code is expected but hand-written overlays, examples, and companion artifacts still matter;
- teams that want one source contract, one reviewable Rust SDK family, and ordinary Cargo/docs.rs/crates.io publication discipline;
- products where outside consumers, not only one internal application, will depend on the SDK surface.

Assumptions:
- stable Rust;
- OpenAPI is already the real contract source or is close enough to be treated that way;
- async HTTP client posture is acceptable;
- docs.rs and crate publication are part of the public support surface;
- the team wants a Rust-native boring default instead of maximum generator-template flexibility.

This is **not** the default for:
- protobuf/gRPC-first SDKs;
- Smithy-first or large official multi-service SDK families;
- one-off internal generated clients with no public semver/support ambition;
- or generic reusable libraries that happen to call HTTP but are not really an SDK family.

## Why this default now
The recurring problem here is not “can Rust generate API clients?”
It is “what boring reviewable lane should a public Rust SDK family normalize around before publication?”

The archive’s current answer for this scope is:

**checked-in OpenAPI contract + `progenitor`-generated async client + thin hand-written overlay/helpers + checked examples/docs + explicit semver/release/package discipline.**

Why this wins here:
- Rust’s latest challenges framing still says ecosystem navigation depends too much on **choice paralysis** and **tacit knowledge**.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey still says online docs remain the preferred canonical reference while editor/LLM-mediated learning rises.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `progenitor` is an opinionated Rust-native OpenAPI client generator and can also generate CLI and `httpmock` helpers.
  https://docs.rs/progenitor
  https://github.com/oxidecomputer/progenitor
- `utoipa` makes a Rust-native code-first OpenAPI source path viable when the API producer is also Rust.
  https://docs.rs/utoipa
- Oxide demonstrates the most legible Rust-native family pattern: one OpenAPI source, checked-in generated code, CLI + SDK + mock family, and CI synchronization.
  https://github.com/oxidecomputer/oxide.rs
- OpenAPI Generator’s Rust lane remains real and flexible, which is exactly why a narrower Rust-native boring default is valuable instead of another giant option matrix.
  https://openapi-generator.tech/docs/generators/rust/
- Cargo semver, docs.rs build behavior, crates.io review surfaces, Trusted Publishing, and the public/private-dependencies goal all make public SDK-family discipline more inspectable than it used to be.
  https://doc.rust-lang.org/cargo/reference/semver.html
  https://docs.rs/about/builds
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://crates.io/docs/trusted-publishing
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Default lane summary
### Default lane
- contract truth: **checked-in OpenAPI document**
- source posture: **spec-first or Rust-owned code-first via `utoipa`, but the emitted OpenAPI document is the reviewable handoff**
- generation posture: **`progenitor`-generated async client**
- ownership posture: **generated surface checked in, with hand-written overlay/helpers kept explicit**
- family posture: **SDK first; optional CLI/mock companions only when they genuinely share the same contract/product story**
- docs posture: **examples/docs are part of the product, not a post-hoc README afterthought**
- release posture: **semver-gated, docs.rs-aware, exact package identity, CI-sync generation discipline**

### Serious alternatives
- **OpenAPI Generator Rust lane** when cross-language parity, runtime-template flexibility, or generator-template customization is central
- **Smithy / smithy-rs lane** when Smithy models, service-per-crate structure, and official large-SDK-family runtime assumptions are the real center
- **gRPC / protobuf lane with `tonic-build`** when protobuf descriptors, not OpenAPI, are the real contract source

### Watch / not-default here
- hiding generation behind macros/build scripts can be acceptable, but it is not the conservative default for a public SDK family when reviewability matters;
- one giant hand-written wrapper over generated code is not the default posture here; keep overlays narrow and visible;
- release automation choice is an overlay decision, not the core lane.

## Slot guidance
### Contract slot
Prefer a checked-in OpenAPI document that the team can diff and review directly.
If the producer is also Rust, `utoipa` is a serious path to that document.
But the **document**, not only the derive macros, should remain the reviewable handoff.

### Generation slot
Prefer `progenitor` for the conservative Rust-native default.
Keep the generated SDK surface reviewable and reproducible.
Checking in generated code is the conservative posture here because it makes source browsing, docs.rs, and human diffs much clearer.

### Ownership slot
Keep generated code and hand-written code visibly separate.
Treat helpers, convenience methods, auth wrappers, or CLI-related extensions as overlays, not silent mutations of the generator output.

### Runtime / auth / config slot
Do not let runtime/config/auth posture disappear into “whatever reqwest does”.
Make default client construction, auth expectations, timeout/retry posture, and environment/profile assumptions explicit in docs and examples.

### Docs / examples slot
Treat docs.rs and checked examples as part of the support surface.
If docs.rs-specific configuration matters, test that path in CI with `cargo docs-rs`.

### Versioning / release slot
Treat SDK-family release truth as distinct from raw contract change.
Use semver review and exact package identity.
If the family includes SDK + CLI + mock companions, make that relationship explicit in versioning and release notes instead of implying they are independent by accident.

## Serious alternatives and when they win
### OpenAPI Generator wins when
- the same upstream spec must drive many languages;
- runtime-template knobs and generator-template customization matter more than a Rust-native opinionated path;
- or a trait-based/middleware-heavy generated client is more important than the narrower Rust-native default.

### Smithy wins when
- Smithy is the source language;
- the SDK family is large enough that multi-service/runtime layering is central;
- or the project needs the Smithy/AWS-style separation between high-level fluent API and lower-level control.

### gRPC / protobuf with `tonic-build` wins when
- protobuf descriptors are the authoritative contract;
- streaming/RPC semantics dominate the client surface;
- or OpenAPI would only be a lossy shadow of the real API product.

## Escalate to a project-specific brief when
- the product spans OpenAPI plus gRPC or plus WebSocket/event streams in one family;
- auth/config/runtime behavior is unusually complex or policy-heavy;
- the SDK surface is split across multiple crates or multiple transport layers;
- you need deliberate CLI + SDK + mock + examples family coordination beyond a small companion layer;
- or the team is deciding between Rust-native generation and a broader multi-language codegen strategy.

## Canonical references
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

## Renewal inputs
Recheck before renewal:
- whether `progenitor` remains the clearest Rust-native boring default for the OpenAPI-shaped public SDK family;
- whether OpenAPI Generator’s Rust lane changes enough to beat the Rust-native opinionated path for this scope;
- whether Oxide-style checked-in generation + CI-sync continues to look like the clearest reviewable family pattern;
- whether Cargo semver/public-dependencies/docs.rs guidance materially changes public SDK-family release discipline;
- whether crates.io review surfaces or Trusted Publishing change the recommended publication/review posture;
- whether the lane should split into **public SDK family** versus **official large generated SDK family**.

## Non-goals
- choosing the one true generator for every Rust API client;
- pretending all generated clients are public SDK families;
- collapsing gRPC, Smithy, and OpenAPI into one fake universal lane;
- or claiming that generation alone solves support, docs, or versioning.
