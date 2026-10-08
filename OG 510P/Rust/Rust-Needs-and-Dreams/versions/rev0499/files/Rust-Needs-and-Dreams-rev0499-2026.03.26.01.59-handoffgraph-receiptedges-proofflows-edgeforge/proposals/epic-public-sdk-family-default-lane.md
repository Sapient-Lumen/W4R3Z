# Epic Proposal: Public SDK family default lane (`cargo sdkcheck` meets maintained defaults)

## One-sentence pitch
Turn the archive’s older SDK-productization frontier into a concrete boring-default lane for public Rust SDK families: contract in, checked generated client out, overlays and examples explicit, release/support truth reviewable.

## Deliverables
- maintained default card for a conservative public SDK family
- first renewal receipt for that card
- a thin evidence path that links:
  - source contract
  - generated client surface
  - hand-written overlays
  - runtime/auth/config posture
  - checked examples / CLI / mocks where present
  - release/versioning/package-identity truth
- future bridge to `cargo sdkcheck` artifacts from `design/sdk-productization-stack.md`

## Why now (signals)
- Rust’s current challenges framing still says ecosystem navigation depends too much on **choice paralysis** and **tacit knowledge**.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 survey still says online docs remain the canonical learning source while editor/LLM mediation rises.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `utoipa` and `progenitor` now make the Rust-native OpenAPI producer/consumer lane concrete.
  https://docs.rs/utoipa
  https://docs.rs/progenitor
- OpenAPI Generator keeps a Rust generator with multiple runtime/template options.
  https://openapi-generator.tech/docs/generators/rust/
- `tonic-build` and `smithy-rs` prove the broader generated-SDK space is real, which makes a bounded maintained default more valuable than another generator comparison.
  https://docs.rs/tonic-build
  https://github.com/smithy-lang/smithy-rs
- Oxide’s Rust SDK/CLI repo demonstrates a practical Rust-native SDK family pattern with checked-in generated code and CI synchronization.
  https://github.com/oxidecomputer/oxide.rs

## Non-goals
- replacing `progenitor`, OpenAPI Generator, `tonic-build`, or `smithy-rs`
- declaring one universal Rust SDK story for every contract family
- pretending generated code alone solves support, docs, or release truth
- flattening public SDK families back into generic publishable-library advice

## Strategic value
This is valuable because it turns a conspicuous archive seam into a concrete answer:
not “what is SDK productization in theory?”
but “what should a real Rust team normalize around for the most common public SDK family right now?”

It also creates a better bridge between:
- contract truth,
- crate-as-product truth,
- public API and semver discipline,
- checked examples/docs,
- and future `sdk-pack` style evidence.
