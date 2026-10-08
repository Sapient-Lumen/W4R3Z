# Design: Polyglot Productization Pilot Program

## Goal
Turn the archive’s **mixed-language Rust product** seam into an executable program instead of scattered good ideas.

The pilot program couples:
- [`design/ffi-boundary-kit.md`](./ffi-boundary-kit.md)
- [`design/host-package-kit.md`](./host-package-kit.md)
- [`design/wasm-component-kit.md`](./wasm-component-kit.md)
- [`design/polyglot-productization-stack.md`](./polyglot-productization-stack.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)

The central thesis is that Rust adoption in existing product estates often fails at **boundary + host-package + support** seams, not because one more binding generator is missing.

## Why this now deserves a pilot program
- The Rust project is now explicitly treating mixed-language adoption as real infrastructure work, not just a tutorial topic.
  - https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
  - https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The ecosystem already has credible lane-specific tools, which is exactly when a productization layer becomes more valuable than another framework bake-off.
  - Python: https://pyo3.rs/main/ ; https://www.maturin.rs/distribution.html
  - mobile bindings: https://mozilla.github.io/uniffi-rs/latest/Getting_started.html
  - Node ABI lane: https://nodejs.org/api/n-api.html
  - C++ bridge/build handoff: https://cxx.rs/build/cargo.html ; https://cxx.rs/build/other.html
  - multi-language components: https://component-model.bytecodealliance.org/composing-and-distributing/composing.html
- The 2025 Rust survey suggests both structural adoption and growing machine-mediated learning/workflows. That is a strong reason to leave behind more canonical, machine-usable product truth.
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Strategic posture
This should be treated as a **companion evidence substrate**, not as a bid to unify all host-language packaging under one tool.

- `cargo ffi` owns native boundary truth.
- `cargo hostpkg` owns foreign package/runtime/support truth.
- `cargo wit` / component tooling owns WIT/component truth.
- Release/support/distribution consumers import these artifacts instead of re-deriving them from README files.

## Ranked pilot order

### Pilot 1 — Python wheel lane
**Shape**
- PyO3 + maturin package published as wheel/sdist.

**Must prove**
- `hostpkg-manifest/v0` can separate Cargo package identity, Python package identity, and module identity.
- wheel tags / manylinux posture / interpreter support become reviewable evidence.
- docs/import transcripts and runtime floors are attachable.

### Pilot 2 — Node addon lane
**Shape**
- Node-API / `napi-rs` addon shipped with JS/TS glue and platform artifacts.

**Must prove**
- ABI/runtime assumptions are explicit.
- JS binding / `.d.ts` / `.node` artifacts have clear provenance.
- Node-API stability can stay separate from external-library caveats.

### Pilot 3 — Generated mobile binding lane
**Shape**
- UniFFI-generated Swift/Kotlin package around a Rust core.

**Must prove**
- generated-binding provenance is explicit.
- thread/lifetime/init restrictions are visible.
- foreign package/module/bundle identities do not collapse into the Cargo package name.

### Pilot 4 — Native handoff lane
**Shape**
- C/C++ consumer imports headers/staticlibs/shared libs plus package/support evidence.

**Must prove**
- `hostpkg-pack/v0` can import `ffi-pack/v0` cleanly.
- build-system handoff stays explicit.
- package/support evidence does not replace ABI truth.

### Pilot 5 — Component lane
**Shape**
- Wasm component or WIT package shipped to a multi-language consumer.

**Must prove**
- component identity and host-package truth stay distinct.
- release/support consumers can read WIT/component facts without pretending they are native ABI artifacts.

The pilot program is now also the proving path for the stack-level proposal direction in [`proposals/epic-polyglot-productization-stack.md`](../proposals/epic-polyglot-productization-stack.md): the goal is not to make one lane win, but to prove that imported boundary/package/release/support truth can survive packaging and consumer handoff honestly.

## Shared artifact family
### Host-package layer
- `hostpkg-manifest/v0`
- `hostpkg-report/v0`
- `hostpkg-pack/v0`

### Imported lower-layer artifacts
- `ffi-manifest/v0`
- `ffi-pack/v0`
- component/WIT package facts
- release/signature/install artifacts
- support/docs/import transcripts

## Cross-kit boundaries
- **FFI Boundary Kit** keeps owning ABI/ownership/layout contracts.
- **Wasm Component Kit** keeps owning WIT/package/composition contracts.
- **Release Truth Stack** keeps owning publication/provenance/install attachments.
- **Support Envelope + DocProof** keep owning support matrices and checked docs/import evidence.
- **Schema Contract Kit** attaches semantic data-type contracts when needed.

## Pilot scorecard
A pilot only graduates if it shows all of the following:
1. **Foreign-consumer legibility** — someone outside the crate can see what they actually install/import.
2. **Diffability** — package/runtime/support drift is reason-coded.
3. **Lane honesty** — Python, Node, mobile, native, and component lanes remain distinct.
4. **Imported-boundary honesty** — ABI/WIT truth is imported, not silently replaced.
5. **Support honesty** — runtime/platform claims are evidence-backed, not demo-backed.

## Anti-goals
- not a universal polyglot runtime;
- not a replacement for PyO3, maturin, `napi-rs`, UniFFI, CXX, or component tooling;
- not a package-upload wrapper that hides runtime/support truth;
- not a fake “bindings support score”.
