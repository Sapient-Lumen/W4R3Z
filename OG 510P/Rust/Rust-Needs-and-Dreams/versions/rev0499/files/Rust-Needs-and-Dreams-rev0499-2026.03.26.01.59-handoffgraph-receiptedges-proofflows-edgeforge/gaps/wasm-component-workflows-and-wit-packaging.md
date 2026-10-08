# Gap: Wasm component workflows and WIT-first packaging in Rust

## What is missing
Rust now has real upstream momentum for WebAssembly Components, but it still lacks a **boring, reviewable contract** for building, composing, diffing, and publishing them.

Today a team can:
- build runnable or library components with plain `cargo build --target=wasm32-wasip2`,
- generate custom-WIT bindings with `wit-bindgen`,
- still use `cargo component` for richer/custom-WIT workflows and Warg publishing,
- inspect and compose with `wasm-tools`,
- resolve package dependencies with `wkg`,
- and publish/fetch packages through OCI or Warg-based tooling.

What is still missing is the shared layer that answers:
- which WIT packages/worlds a project intends to ship,
- what component surface it actually exported/imported,
- which imports remain unresolved after build,
- how a deployment/runtime intends to satisfy those imports,
- which build lane or adapter path produced the artifact,
- what changed semantically across WIT/component revisions,
- and what publication/package identity downstream tools should trust.

## Why it matters now
This is no longer speculative niche tooling.

Rust’s 2026 goals make **Wasm Components** a flagship area and explicitly call for adding/stabilizing three compiler targets plus Wasm-specific language experimentation. Rust already ships `wasm32-wasip2` as a Tier 2 target, and the official component-model guide now says Rust has first-class component targets, shows native Cargo builds, and says `cargo-component` is being deprecated as native tooling can be used directly. But that same guide also says the toolchain cannot yet auto-generate custom-WIT bindings. That means the ecosystem is in a transition phase, not a settled one.

The workflow boundary remains fragmented in precisely the way that creates room for an epic companion contribution:
- plain Cargo builds can emit components,
- `wit-bindgen` still matters for custom-WIT binding generation,
- `cargo component` still matters for richer/custom-WIT workflows and Warg publishing,
- composition and unresolved imports remain a distinct operational step,
- registry/package identity lives in separate tools,
- and host/runtime assumptions remain easy to lose.

That fragmentation is tolerable for experts and rough for everyone else.

## Existing building blocks worth composing
- Rust’s 2026 flagship goals explicitly include Wasm Components, including compiler-target work and Wasm-specific language experimentation.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Rust 1.82 made `wasm32-wasip2` Tier 2, which means direct compiler support for WASI 0.2 components is part of the mainstream toolchain.
  https://blog.rust-lang.org/2024/11/26/wasip2-tier-2/
- The official component-model Rust guide now shows native `wasm32-wasip2` Cargo builds, says `cargo-component` is being deprecated as native tooling can be used directly, and also notes that custom-WIT bindings still require `wit-bindgen`.
  https://component-model.bytecodealliance.org/language-support/building-a-simple-component/rust.html
- `cargo component` remains experimental and still carries important adaptation/package workflows that upstream Cargo does not yet subsume completely, including Warg publishing and custom rust-analyzer check-command posture.
  https://github.com/bytecodealliance/cargo-component
- `wasm-pkg-tools` / `wkg` already support OCI and Warg registries, expose a shared config format, and write a standardized `wkg.lock` meant for reuse by language-specific tooling.
  https://docs.rs/crate/wasm-pkg-common/0.13.0
- Warg already exists as a registry protocol/reference implementation for distributing components and interfaces.
  https://github.com/bytecodealliance/registry
- `wit-bindgen` and `wasm-tools` already provide the binding-generation and inspection primitives.
  https://docs.rs/wit-bindgen
  https://github.com/bytecodealliance/wasm-tools

## Why existing tools are not yet the whole answer
The ecosystem has **real tools**, but not one **stable contract/evidence layer**.

Today teams still invent local answers for:
- component subject identity,
- WIT lock/baseline format,
- import-satisfaction/composition reporting,
- host-requirement summaries,
- compatibility reason codes,
- publication/package identity,
- and CI-friendly release artifacts.

That is the familiar archive pattern: strong point tools, weak shared artifacts.

## Target outcome
A project should be able to say:
- “this package ships these WIT worlds/interfaces,”
- “this component was produced through this build lane,”
- “these imports remain unresolved, or are satisfied by this composition plan/run,”
- “these are the host requirements a runtime must meet,”
- “this version changed the interface in these precise ways,”
- and “this is the portable bundle CI, release tooling, registries, and hosts can consume.”

That is bigger than a binding generator and smaller than trying to standardize the whole Wasm ecosystem in one move.


## Archive decision
The next credible archive move is a ranked pilot program rather than a bigger abstract schema list: native Cargo export lane first, `cargo-component` bridge second, composition/host requirements third, registry/package identity fourth, and downstream consumer imports last. See [`design/wasm-component-pilot-program.md`](../design/wasm-component-pilot-program.md).
