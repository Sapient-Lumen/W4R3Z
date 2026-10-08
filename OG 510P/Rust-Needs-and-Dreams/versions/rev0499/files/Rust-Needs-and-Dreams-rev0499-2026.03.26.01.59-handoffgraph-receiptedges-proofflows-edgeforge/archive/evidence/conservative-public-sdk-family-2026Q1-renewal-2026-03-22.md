# Renewal receipt: Conservative public SDK family (2026-03-22)

Card under review:
- `defaults/conservative-public-sdk-family-2026Q1.md`

Review goal:
- decide whether the archive should publish a first maintained **public SDK family** card;
- decide whether the clearest boring current default for the bounded OpenAPI-shaped public SDK lane is **checked-in OpenAPI contract + `progenitor`-generated client + thin hand-written overlay/helpers**;
- and keep contract truth, generated-code truth, runtime/auth/config truth, docs/example truth, and release/versioning/package truth visibly separate.

## Canon import checked
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `utoipa`:
  https://docs.rs/utoipa
- `progenitor` docs and repo:
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
- crates.io development update and Trusted Publishing:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://crates.io/docs/trusted-publishing
- public/private dependencies goal:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Fresh observations
1. Official Rust signals still say the ecosystem navigation problem is partly about **choice paralysis** and **tacit knowledge**, which supports publishing a bounded public SDK-family default rather than leaving the lane to generator folklore.
2. `progenitor` is now clearly more than a single client stub macro: docs and repo material show opinionated OpenAPI 3.0.x client generation plus optional CLI and `httpmock` helper generation.
3. OpenAPI Generator’s Rust lane remains broad and configurable enough to stay a serious alternative rather than being hand-waved away.
4. `smithy-rs` and the AWS SDK for Rust remain strong evidence that generated SDKs are product families with configuration, examples, and runtime layering, not just generated method stubs.
5. Oxide remains the clearest concrete Rust-native proof point for this lane: one OpenAPI source, checked-in generated code, CLI + SDK + mock family, CI sync, and explicit versioning policy.
6. Cargo semver guidance, docs.rs build behavior, crates.io Security-tab/source/trusted-publishing surfaces, and the public/private-dependencies goal make public SDK families more reviewable than they used to be.

## Slot-by-slot review
### Contract truth
The lane needs a checked-in OpenAPI document that can be reviewed and diffed directly.
`utoipa` is a valid producer-side path when the API source is also Rust, but the emitted contract should still remain the reviewable handoff.

### Generated-code truth
`progenitor` is the clearest Rust-native boring default for this narrow OpenAPI-shaped lane.
Checking in generated code remains the conservative review posture because it keeps source browsing, docs.rs, and human diffing legible.

### Hand-written overlay truth
A public SDK family is not only generator output.
Helpers, auth wrappers, convenience methods, and companion CLI/mock artifacts should remain explicit overlays rather than disappearing into opaque generation steps.

### Runtime / auth / config truth
Runtime construction and auth/config assumptions are part of the public product.
They should not be left implicit in generated code or scattered README prose.

### Docs / examples truth
Docs.rs and checked examples are part of the support envelope.
If docs.rs metadata matters, the lane should treat `cargo docs-rs` style checking as a normal part of CI.

### Release / versioning / package truth
SDK-family release truth is not identical to raw contract truth.
Package identity, semver review, and explicit family relationships matter more here than in a private generated client.

## Serious alternatives retained
- **OpenAPI Generator Rust** — strongest alternative when cross-language parity or template/runtime flexibility is central.
- **Smithy / smithy-rs** — strongest alternative when Smithy is the source language or the SDK family is large and official enough to need that posture.
- **gRPC / protobuf with `tonic-build`** — strongest alternative when protobuf descriptors are the real contract source.

## Judgment
Publish the card as a maintained public default.

Label:
- **default-with-caveats**

Why:
- the project class recurs often;
- the archive already had the higher-level SDK-productization theory but still lacked a maintained public answer;
- and the evidence supports a bounded conservative default without pretending the entire SDK landscape has converged.

## Replay notes
- renew when `progenitor`, OpenAPI Generator, or Cargo/docs.rs/crates.io guidance changes enough to move the boring default for this bounded scope;
- renew when a Rust-native checked-in-generation pattern stronger than the current Oxide-style proof point becomes widely legible;
- split the lane when the archive is ready for a separate **official large generated SDK family** card or a separate **gRPC/protobuf public SDK** card.
