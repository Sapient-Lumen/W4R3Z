# Gap: Public SDK families need a boring Rust default above raw generation

## What is missing
Rust already has strong point tools for generated or contract-driven SDK work.
What it still lacks is a maintained, reviewable **boring default lane** for the public SDK family that many teams actually need:
- one upstream API contract,
- one Rust SDK crate family,
- optional CLI/mock companions,
- checked examples and docs,
- and a release/versioning story that survives regeneration.

## Why it matters
Without this lane, teams still rediscover the same painful questions:
- Is the OpenAPI file itself the source of truth, or is the generated Rust surface?
- Should generated code be checked in, regenerated in CI, or hidden behind macros/build scripts?
- How should hand-written helpers and auth/config wrappers coexist with generated code?
- What counts as a semver change when the contract changed versus when generation changed?
- How should CLI/mock companions relate to the SDK crate?
- Where should docs.rs, examples, and package identity fit into review?

Those questions are not fully answered by a generator homepage.
They are product questions.

## Existing building blocks worth composing
- `utoipa` provides a code-first OpenAPI path in Rust.
  https://docs.rs/utoipa
- `progenitor` provides opinionated OpenAPI → Rust client generation and can also generate CLI and `httpmock` helpers.
  https://docs.rs/progenitor
  https://github.com/oxidecomputer/progenitor
- OpenAPI Generator maintains a Rust lane with multiple runtime/template choices.
  https://openapi-generator.tech/docs/generators/rust/
- `tonic-build` proves protobuf/gRPC code generation is already a normal Rust workflow.
  https://docs.rs/tonic-build
- `smithy-rs` and the AWS SDK for Rust prove generated SDK families are real products at scale.
  https://github.com/smithy-lang/smithy-rs
  https://docs.aws.amazon.com/sdk-for-rust/latest/dg/welcome.html
- Oxide shows a practical Rust-native pattern where SDK, CLI, and mock family artifacts derive from one checked-in OpenAPI source and stay synchronized in CI.
  https://github.com/oxidecomputer/oxide.rs

## Why existing tools are not yet the whole answer
The ecosystem has generation tools.
It still lacks the **boring public default lane** that says how to combine them responsibly for the recurring OpenAPI-shaped public SDK family.

The missing contribution is not another generator.
It is the thin lane above generators that preserves:
- source contract truth,
- generated code truth,
- hand-written overlay truth,
- runtime/auth/config truth,
- docs/example/mock truth,
- and release/versioning/package truth.

## Target outcome
A project should be able to say:
- “this OpenAPI contract is the source for our Rust SDK family,”
- “this generated client is checked and reviewable,”
- “these helpers/examples/CLI/mocks are the supported overlay,”
- “this is how release/versioning treats contract versus generation change,”
- and “this is the boring default path a Rust consumer can trust first.”
