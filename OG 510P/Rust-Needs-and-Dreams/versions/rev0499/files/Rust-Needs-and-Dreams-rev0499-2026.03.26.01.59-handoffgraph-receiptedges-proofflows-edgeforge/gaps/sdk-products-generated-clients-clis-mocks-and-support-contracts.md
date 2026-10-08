# Gap: SDK products, generated clients, CLIs, mocks, and support contracts

## What is missing
Rust has credible ingredients for **schema-driven and contract-driven client generation**, but it still lacks a **boring product boundary** for shipping and maintaining Rust SDKs.

Today teams can separately:
- generate OpenAPI descriptions from Rust services with `utoipa`,
- generate Rust clients from OpenAPI with `progenitor` or OpenAPI Generator,
- generate protobuf/gRPC clients with `tonic-build`,
- generate official large-scale SDKs with Smithy (`smithy-rs` / AWS SDK for Rust),
- and hand-roll HTTP clients with `reqwest` or transport-aware stacks.

What is still missing is the shared layer that answers:
- what SDK surfaces a project officially ships,
- which operations/config/auth/retry/pagination/streaming claims are part of that product surface,
- how crates, CLIs, and mocking/testing helpers relate to one another,
- how generated and hand-written code are tracked across releases,
- what support/docs/versioning guarantees downstream users can rely on,
- and what portable pack release/review tooling should consume.

## Why it matters
This is not just code generation.

Rust is increasingly used where **API products** matter: server backends, web/networking services, and cloud technologies are prominent usage domains in the Rust survey, and the ecosystem now includes serious Rust-facing API products rather than only internal services.

The pain is familiar:
- generated clients drift from their source contracts,
- auth/config/retry behavior is partly generated and partly hand-written,
- support truth lives in README prose,
- CLIs and mock helpers share a contract source but not a reviewable product model,
- and release/versioning practice is often ad hoc even when the underlying protocol diff is not.

A worthy contribution here would make Rust SDKs easier to **review, version, publish, support, and regenerate** without anointing one generator or one service style as the universal answer.

## Existing building blocks worth composing
- `utoipa` already provides code-first OpenAPI generation for Rust REST APIs and aims to be the place to go for OpenAPI documentation in Rust codebases.
  https://docs.rs/utoipa
- `progenitor` already generates opinionated Rust clients from OpenAPI 3.0.x descriptions.
  https://docs.rs/progenitor
- OpenAPI Generator already supports a Rust client lane with multiple HTTP-library options (`hyper`, `reqwest`, `reqwest-trait`) and middleware/config choices.
  https://openapi-generator.tech/docs/generators/rust/
- `tonic` and `tonic-build` already make codegen the normal path for gRPC clients and servers in Rust.
  https://docs.rs/tonic
  https://docs.rs/tonic-build
- `smithy-rs` already generates clients, servers, and the AWS SDK for Rust, proving the problem is real at ecosystem scale.
  https://github.com/smithy-lang/smithy-rs
  https://smithy-lang.github.io/smithy-rs/design/
- The AWS SDK for Rust already has explicit configuration, examples, and maintenance/support documentation, which is a reminder that a real SDK is more than generated method stubs.
  https://docs.aws.amazon.com/sdk-for-rust/latest/dg/welcome.html
- Oxide’s Rust SDK/CLI repo is especially instructive: the CLI, SDK, and mocking library are all derived from an OpenAPI description; generated code is checked in; CI keeps the source spec and generated output in sync; and versioning explicitly accounts for both API incompatibilities and generation incompatibilities.
  https://github.com/oxidecomputer/oxide.rs

## Why existing tools are not yet the whole answer
The ecosystem has **generators and transport/runtime building blocks**, but not the **shared SDK product layer**:
- OpenAPI tools describe and generate HTTP-facing surfaces.
- Smithy proves large-scale SDK generation is possible.
- tonic/prost prove the gRPC path is healthy.
- reqwest/hyper/tower provide runtime composition.
- library/release/support tooling already exists elsewhere in the archive.

But teams still have to invent their own answers for:
- normalized SDK surface identity,
- operation-to-contract provenance,
- generated-versus-hand-written ownership boundaries,
- auth/config/retry support declarations,
- CLI/SDK/mock family relationships,
- SDK-specific diff reason codes,
- and release attachment conventions that survive regeneration.

That is the same pattern seen elsewhere in this archive: strong point tools, weak shared artifacts.

## Target outcome
A project should be able to say:
- “these are the SDK products this service or platform officially ships,”
- “these crates/CLIs/mocks derive from these specific service/schema/protocol contracts,”
- “these config/auth/retry/pagination/streaming behaviors are part of the supported SDK surface,”
- “this release changed the SDK in these precise ways and for these reasons,”
- and “this is the portable bundle CI, release, support, docs, and downstream users can consume.”

That is bigger than a generator template and smaller than a full platform framework.
