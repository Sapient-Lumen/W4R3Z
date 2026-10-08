# Gap: publishable library defaults, docs.rs truth, semver gates, and public API discipline

## The gap
Rust has strong building blocks for publishing libraries, but still lacks a boring shared answer to:
- what should a reusable crate prove before release?
- what public API boundary mistakes should be treated as contract mistakes instead of “future cleanup”?
- how should docs.rs behavior be tested before publish?
- how should exact crate identity and supply-chain review be kept visible in release discipline?

## Why this is still missing
The relevant truth is spread across:
- Cargo manifest docs,
- Cargo semver docs,
- docs.rs metadata/build docs,
- crates.io review surfaces,
- `cargo-semver-checks`,
- and maintainer custom workflows.

That fragmentation is tolerable for experts and bad for the broader ecosystem.

## What a worthy contribution looks like
A worthy contribution is a **thin reviewable publishable-library lane** that keeps these distinct:
- manifest truth,
- docs.rs truth,
- public API / dependency exposure truth,
- semver gate truth,
- registry / supply-chain truth,
- renewal receipt truth.

## What would not count
- another generic “how to publish a crate” tutorial alone;
- a hidden score for package quality;
- one more release bot with weak contract modeling;
- or an assistant answer that cannot be renewed later.
