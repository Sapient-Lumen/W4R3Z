# Gap: installable CLI products, release routes, ownership scope, and update posture

## The gap
Rust has strong building blocks for command-line products, but still lacks a boring shared answer to:
- how should a public CLI be released so prebuilt binaries, source fallback, and ownership remain explicit?
- which install routes should be considered part of the default support envelope?
- when should `cargo install --locked` be treated as a real documented path rather than lore?
- when is `cargo-binstall` support worth the maintenance cost?
- how should update/uninstall promises be stated when lifecycle behavior remains route-specific?

## Why this is still missing
The relevant truth is spread across:
- Cargo install/uninstall/package docs,
- release-tool docs,
- README snippets,
- and maintainer habit.

That fragmentation is tolerable for experts and bad for the broader ecosystem.

## What a worthy contribution looks like
A worthy contribution is a **thin reviewable installable-CLI lane** that keeps these distinct:
- release/build truth,
- supported install routes,
- source-fallback truth,
- optional Cargo-native prebuilt route truth,
- supply-chain receipt truth,
- ownership/update truth,
- renewal receipt truth.

## What would not count
- another generic “ship your CLI” tutorial alone;
- a release bot with weak route modeling;
- a universal installer/updater claim;
- or an assistant answer that cannot be renewed later.
