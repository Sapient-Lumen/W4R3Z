# Epic Proposal: SDK Productization Stack (`cargo sdkcheck`)

## One-sentence pitch
Turn Rust SDK families into first-class product artifacts: export their supported surface, link them to upstream contracts, record auth/runtime profiles and checked examples, diff their changes, and ship the result as a portable pack.

## Deliverables
- `cargo-sdkcheck` reference implementation
- Schemas / artifacts:
  - `sdk-surface/v0`
  - `sdk-operation-map/v0`
  - `sdk-runtime-profile/v0`
  - `sdk-auth-profile/v0`
  - `sdk-check-report/v0`
  - `sdk-diff-report/v0`
  - `sdk-pack/v0`
- Adapters / integrations:
  - OpenAPI import lanes (`utoipa`, `progenitor`, OpenAPI Generator)
  - Smithy import lane (`smithy-rs` metadata / sidecar export where feasible)
  - gRPC/protobuf lane (`tonic-build` / descriptor imports)
  - runtime/auth imports from existing Runtime Settings / Identity / Credentials work
  - release/support imports from Library Productization / Release Truth / Support Envelope
- Docs:
  - SDK compatibility policy guide
  - generated-versus-hand-written ownership guide
  - release/support examples for SDK + CLI + mock families

## Why now (signals)
- The 2024 State of Rust survey says Rust is especially popular for server backends, web/networking services, and cloud technologies.
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while LLM/editor workflows are rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `utoipa` and `progenitor` show a credible Rust-native OpenAPI producer/consumer lane.
  https://docs.rs/utoipa
  https://docs.rs/progenitor
- OpenAPI Generator keeps a Rust client lane alive with multiple runtime templates and middleware options.
  https://openapi-generator.tech/docs/generators/rust/
- `tonic` and `tonic-build` show that gRPC/protobuf client/server generation is already normal in Rust.
  https://docs.rs/tonic
  https://docs.rs/tonic-build
- `smithy-rs` already generates clients, servers, and the AWS SDK for Rust, but explicitly says its internal and external interfaces are unstable; that is exactly the kind of reality a product layer should describe without hiding.
  https://github.com/smithy-lang/smithy-rs
- The AWS SDK for Rust docs include configuration, examples, and maintenance/support references, showing that an SDK is more than generated type definitions.
  https://docs.aws.amazon.com/sdk-for-rust/latest/dg/welcome.html
- Oxide’s Rust SDK/CLI repo demonstrates a practical Rust-native product family derived from one OpenAPI source, with checked-in generated code and CI synchronization.
  https://github.com/oxidecomputer/oxide.rs

## Non-goals
- Replacing OpenAPI, Smithy, or protobuf/gRPC source contracts
- Replacing `progenitor`, OpenAPI Generator, `tonic-build`, or `smithy-rs`
- Standardizing one universal auth framework or HTTP runtime
- Pretending all SDKs are codegen-only or all support stories are identical
- Solving every platform-control-plane or vendor-specific SDK need in one mega-tool

## Strategic value
This stack has strong leverage because it connects:
- upstream contract truth,
- Rust crate-as-product truth,
- auth/config/runtime ergonomics,
- checked examples and support/docs truth,
- release/versioning posture,
- and downstream migration/support/review consumers.

It also fills a conspicuous hole in the archive: the layer where a service or protocol stops being only a producer concern and becomes a **supported Rust API product**.

## Milestones
1. **v0**
   - export `sdk-pack/v0`
   - support one OpenAPI lane end-to-end
   - stable SDK diff reason codes
2. **v0.2**
   - add Smithy and gRPC/protobuf attachment lanes
   - add runtime/auth profile imports
   - add checked example and CLI/mock family support
3. **v1**
   - richer release/support integrations
   - better compatibility guidance by source-contract family
   - conformance corpus for SDK diff/report behavior
