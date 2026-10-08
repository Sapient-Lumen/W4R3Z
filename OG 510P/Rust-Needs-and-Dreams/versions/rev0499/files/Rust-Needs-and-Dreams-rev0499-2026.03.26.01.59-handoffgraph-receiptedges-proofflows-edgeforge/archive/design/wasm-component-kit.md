# Design: Wasm Component Kit (`cargo wit`, `component-pack/v0`)

## Goal
Define a portable **WIT/package/composition/release contract** for Rust WebAssembly Components so plain Cargo, `cargo-component`, `wit-bindgen`, `wkg`, `wasm-tools`, and runtime hosts can exchange one reviewable set of artifacts.

This should **not** replace compiler targets, `cargo-component`, `wit-bindgen`, `wkg`, `wasm-tools`, Wasmtime, or registry protocols. It should make them easier to compose coherently and make their outputs reviewable.

## References (signals)
- Rust’s 2026 flagships explicitly include **Wasm Components**, including adding and stabilizing three compiler targets and beginning experimentation with Wasm-specific language features.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Rust 1.82 made `wasm32-wasip2` Tier 2, which means direct compiler support for building WASI 0.2 components is now part of the mainstream toolchain.
  https://blog.rust-lang.org/2024/11/26/wasip2-tier-2/
- The official component-model Rust guide now says Rust has first-class support for core Wasm and components via toolchain targets, shows `cargo build --target wasm32-wasip2`, and says `cargo-component` is being deprecated as native tooling can be used directly. The same guide also says the toolchain cannot yet auto-generate bindings for custom WIT, so `wit-bindgen` still matters.
  https://component-model.bytecodealliance.org/language-support/building-a-simple-component/rust.html
- `cargo component` remains experimental, still uses adaptation flows that plain upstream Cargo does not yet subsume completely, still publishes to Warg, and still asks rust-analyzer users to override the check command for some workflows.
  https://github.com/bytecodealliance/cargo-component
- `wasm-pkg-tools` / `wkg` already support OCI and Warg registries, expose a shared config format, and write a standardized `wkg.lock` intended for reuse by other language-specific tooling.
  https://docs.rs/crate/wasm-pkg-common/0.13.0
- Warg already exists as a registry protocol/reference implementation for distributing components, interfaces, and core modules.
  https://github.com/bytecodealliance/registry
- `wit-bindgen` and `wasm-tools` remain the key binding-generation and inspection primitives.
  https://docs.rs/wit-bindgen
  https://github.com/bytecodealliance/wasm-tools

## Design principles
1. **Keep crate identity separate from component identity.** A Cargo package is not the same thing as a WIT package/world surface.
2. **Keep build lane separate from composition lane.** “I emitted a component” and “its imports are satisfied in this deployment/runtime” are different truths.
3. **Treat import satisfaction as evidence.** Unresolved imports, adapters, and runtime-provided worlds should be preserved, not hand-waved away.
4. **Preserve raw WIT and inspection truth.** Attach `wit`, `wkg.toml`, `wasm-tools` outputs, and component metadata rather than flattening them into one invented schema.
5. **Separate host requirements from host policy.** A component may require `wasi:cli/run` or filesystem-related interfaces without itself proving what sandbox/policy a given host enforces.
6. **Treat publication as its own layer.** Registry/package identity, digests, and provenance should not be hidden inside build logs.
7. **Stay plural about registries and hosts.** OCI, Warg, local/git baselines, Wasmtime, and other hosts all matter.

## Artifact set
### 1) `component-subject/v0`
Declares the thing being discussed:
- Cargo package/workspace identity
- crate role (`command-component`, `library-component`, `adapter`, `host`)
- WIT package/worlds in scope
- build lane (`plain-cargo-wasip2`, `cargo-component`, adapted core-wasm lane, etc.)
- intended publication/runtime lane

This is the human-review starting point.

### 2) `wit-resolution-lock/v0`
Machine-readable WIT/package resolution truth:
- resolved WIT dependency graph
- source provenance (path/git/OCI/Warg/other)
- `wkg` / registry configuration attachments
- tool versions (`rustc`, `cargo-component`, `wit-bindgen`, `wkg`, `wasm-tools` when relevant)
- hashes for WIT inputs and produced component artifacts

Design rule: WIT resolution must not remain a hidden side effect.

### 3) `component-surface-report/v0`
What the produced component actually exposes:
- exported worlds/interfaces/resources/functions
- imported worlds/interfaces/resources/functions
- unresolved-import state
- target/build-lane truth
- component metadata and `wasm-tools` inspection attachments
- produced artifact digests

This is the reviewable surface artifact.

### 4) `component-host-requirement-profile/v0`
What a host/runtime must satisfy:
- required well-known worlds/interfaces (`wasi:cli/run`, custom worlds, resources, etc.)
- adapter assumptions
- import families by kind (runtime-provided, composition-provided, package-provided)
- broad host capability labels
- non-goals / unsupported host expectations

Design rule: requirement labels are not a substitute for Runtime Capability or Policy evidence.

### 5) `composition-plan/v0`
How imports are intended to be satisfied:
- unresolved imports at build time
- composition graph / fulfillment plan
- runtime-provided versus package/component-provided imports
- local vs registry-sourced dependencies
- adapter or glue modules involved

### 6) `composition-run-report/v0`
What composition actually did:
- toolchain/runtime used
- input artifacts and digests
- successful or failed satisfactions
- final self-contained artifact summary when applicable
- reason codes and attachments on failure

This is the missing bridge between “I built a component” and “I can ship/run/embed it”.

### 7) `component-compat-report/v0`
Machine-readable compatibility decisions:
- comparison target and policy mode
- WIT/world/interface/resource diff summary
- pass/fail outcome and reason codes
- import/export drift
- host-requirement widening or narrowing
- toolchain provenance

### 8) `component-publish-report/v0` (optional)
Publication/distribution evidence:
- target registry/protocol (`oci`, `warg`, local mirror, etc.)
- published package identity
- attached component/WIT digests
- provenance/signature references when available
- release attachment list

### 9) `component-vectors/v0` (optional)
Portable small fixtures:
- example invocations
- WIT-level request/response vectors
- composition fixtures
- conformance or minimized repro attachments

### 10) `component-pack/v0`
Bundle format:
- `component-subject/v0`
- `wit-resolution-lock/v0`
- `component-surface-report/v0`
- optional `component-host-requirement-profile/v0`
- optional `composition-plan/v0`
- optional `composition-run-report/v0`
- optional `component-compat-report/v0`
- optional `component-publish-report/v0`
- optional `component-vectors/v0`
- produced component binaries / WIT attachments / digests / provenance pointers

## Reference UX
- `cargo wit init`
- `cargo wit resolve`
- `cargo wit export`
- `cargo wit diff --against <git|artifact|registry>`
- `cargo wit compose`
- `cargo wit publish-report`
- `cargo wit pack`

Design rule: this should start as an adapter/orchestration/report layer. It does not need to replace `cargo-component`; it should bridge the transition between native Cargo-first lanes and the still-important `cargo-component` / `wkg` ecosystem honestly.

## What the kit should provide to others
- **Component authors:** one stable way to export, diff, and publish what they ship.
- **Host authors:** machine-readable import and host-requirement truth.
- **Platform teams:** reusable CI/release artifacts for plugin ecosystems and deployable components.
- **Polyglot users:** WIT/package metadata and registry/configuration truth that is not Rust-only.
- **Tool authors:** stable inputs for Policy, Runtime Capability, Support Envelope, Release Pipeline, Plugin Surface, and Incident workflows.

## Overlap boundaries
- **Not Plugin Surface Kit:** plugin ecosystems care about extension points, host lifecycle, compatibility ranges, and capability handshakes. Wasm Component Kit owns WIT/package/composition/publication truth for the component-model lane.
- **Not Runtime Capability Kit:** that kit owns least-privilege/runtime authority posture. Wasm Component Kit only records host-facing interface/capability requirements.
- **Not FFI Boundary Kit:** that kit is about native ABI/header/contracts across Rust↔C/C++; Wasm Component Kit is about WIT-described component boundaries and composition.
- **Not Support Envelope Kit:** support claims for targets/hosts should attach `component-pack/v0`, not be replaced by it.
- **Not Release Pipeline Kit:** release tooling should attach `component-publish-report/v0` / `component-pack/v0`, not absorb the whole boundary.
- **Not browser-focused `wasm-bindgen` UX:** keep component-model / WASI / WIT workflows distinct from browser-JS interop.

## Execution note
Use [`design/wasm-component-pilot-program.md`](./wasm-component-pilot-program.md) as the ranked rollout: native Cargo export first, `cargo-component` bridge second, composition/host requirement third, registry/package identity fourth, and runtime/release/policy consumers fifth.

## Hard problems (explicitly scoped)
1. **The ecosystem is still in transition**
   - upstream Cargo/targets are improving while `cargo-component` remains important; v0 must compose with both instead of pretending one has already won.
2. **Identity is layered**
   - Cargo package identity, WIT package identity, component artifact identity, and published package identity are not interchangeable.
3. **Hosts differ materially**
   - a host/runtime may satisfy imports in different ways; v0 should preserve requirement truth without inventing one universal host model.
4. **Registries are plural**
   - OCI, Warg, git, and local baselines all matter; v0 should not hard-code one publication story.
5. **Composition is operationally important**
   - import satisfaction, adapter use, and runtime-provided interfaces are as important as ordinary export diffs.
6. **The transition itself is part of the design problem**
   - native `wasm32-wasip2`, `wit-bindgen`, `cargo-component`, `wkg`, and runtime hosts all matter right now; v0 should preserve which lane produced which truth instead of pretending the migration is complete.
