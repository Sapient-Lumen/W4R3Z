# Design: Host Package Kit (`cargo hostpkg`, `hostpkg-pack/v0`)

## Goal
Make Rust-produced **foreign-consumer packages** auditable, regenerable, diffable, and supportable by defining:
- a reference CLI (`cargo hostpkg`),
- a machine-readable host-package manifest (`hostpkg-manifest/v0`),
- a reviewable host-package report (`hostpkg-report/v0`),
- and an attachable package bundle (`hostpkg-pack/v0`).

This is **not** another binding generator.
It is the missing contract layer above lane-specific tools such as PyO3/maturin, `napi-rs`, UniFFI, C/C++ handoff tools, and Wasm-component packaging.

## References (signals)
- Rust safety-critical interop note:
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- C++/Rust interop problem-space mapping goal:
  https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- Rust 2026 flagships include **Wasm Components**:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Rust/component-model guidance now says native `wasm32-wasip2` support is first-class:
  https://component-model.bytecodealliance.org/language-support/rust.html
- `cargo-component` still matters for custom-WIT lanes and explicitly says it remains experimental:
  https://github.com/bytecodealliance/cargo-component
- PyO3 user guide and build/distribution guidance:
  https://pyo3.rs/main/
  https://pyo3.rs/main/building-and-distribution
- maturin explicitly supports PyO3, cffi, UniFFI, and Rust-binary Python packages, while its distribution docs make cross-compilation and `manylinux` / `musllinux` posture first-class:
  https://github.com/PyO3/maturin
  https://www.maturin.rs/distribution.html
- UniFFI getting-started, design-principles, and interface docs:
  https://mozilla.github.io/uniffi-rs/latest/Getting_started.html
  https://mozilla.github.io/uniffi-rs/latest/internals/design_principles.html
  https://mozilla.github.io/uniffi-rs/0.27/udl/interfaces.html
- Node-API ABI-stability docs:
  https://nodejs.org/api/n-api.html
- CXX Cargo and external-build guidance:
  https://cxx.rs/build/cargo.html
  https://cxx.rs/build/other.html
- Wasm Component Model overview:
  https://component-model.bytecodealliance.org/composing-and-distributing/composing.html
  https://component-model.bytecodealliance.org/design/why-component-model.html
- 2025 State of Rust survey on canonical docs / LLM shift:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Core UX: `cargo hostpkg`
- `cargo hostpkg inspect`
  - detect foreign package names/modules, host runtime targets, generated-binding lanes, package metadata, and imported boundary artifacts
- `cargo hostpkg verify`
  - check that generated bindings, package metadata, host-runtime constraints, and shipped artifacts match source + policy
- `cargo hostpkg diff <A> <B>`
  - compare two releases at the **foreign-consumer** surface rather than only at Rust API level
- `cargo hostpkg pack`
  - emit `hostpkg-pack/v0` for review, release, docs, or downstream packaging consumers
- `cargo hostpkg doctor`
  - explain missing wheel tags, ABI/runtime mismatches, stale generated bindings, host-package metadata drift, or support-claim gaps

`cargo hostpkg` should begin as an **inspector / verifier / packer**.
It should not pretend to be the one true generator, package publisher, host-runtime abstraction, or foreign package manager.

## Lane model
`cargo hostpkg` should model multiple host lanes explicitly instead of flattening them:
- **Python package lane**
  - PyO3 / maturin / cffi-style packaging
  - split explicitly into the sublanes described in `design/python-host-lane-map.md`: full-CPython extension, `abi3` limited-API extension, free-threaded extension, and `asyncio` bridge posture
  - wheel/sdist metadata, interpreter targets, manylinux/musllinux posture, module names, stub files, link/test caveats
- **Node addon lane**
  - Node-API / `napi-rs`
  - addon artifact identity, package.json bindings, JS/TS glue, ABI/runtime assumptions, prebuild matrices
- **Generated mobile binding lane**
  - UniFFI Kotlin / Swift / Python output
  - interface identity, generated-binding provenance, foreign package/module names, thread/lifetime restrictions, integration notes
- **Native handoff lane**
  - headers, static/shared libraries, C/C++ bridge products
  - should import `ffi-pack/v0` rather than redefining ABI truth
- **Component package lane**
  - Wasm component / WIT package / registry publication
  - should import component identity and WIT truth rather than pretending it is a native ABI lane
  - should preserve the difference between plain `cargo build --target wasm32-wasip2` paths and custom-WIT / `cargo-component` paths

## Artifacts
### `hostpkg-manifest/v0`
- Cargo package identity + version + toolchain
- foreign package identity:
  - package names, scopes/namespaces, module names, bundle names, WIT package identities as applicable
- lane classification:
  - python / node / generated-mobile / native-handoff / component
- imported boundary artifacts:
  - `ffi-manifest`, WIT/package metadata, generated-binding inputs, schema/runtime attachments
- runtime assumptions:
  - interpreter/runtime version floors
  - ABI family expectations
  - threading / init / callback / async posture
  - error-surface posture
- platform/support claims:
  - OS/arch/libc tags, SDK constraints, simulator/device splits, package-manager expectations
- shipped artifacts:
  - wheels, `.node` binaries, headers, static/shared libs, generated sources, WIT packages, docs/stubs

### `hostpkg-report/v0`
- breakage classification:
  - foreign package rename/split/merge
  - generated-binding drift
  - runtime/ABI/support changes
  - shipped-artifact changes
  - imported-boundary drift
- severity hints:
  - likely packaging-only
  - likely runtime/support-affecting
  - likely foreign-API breaking
- remediation hints:
  - regenerate bindings
  - rebuild wheel/prebuild matrix
  - update host runtime floor
  - refresh docs/stubs/examples

### `hostpkg-pack/v0`
- `hostpkg-manifest.json`
- host-package metadata snapshot
- generated bindings / stubs / JS glue / package manifests / packaging configs
- imported `ffi-pack` / component-pack references where applicable
- support notes and checked install/import transcripts
- provenance: source revision, generator versions, toolchain tuple, host-runtime targets

## Integration points
- **FFI Boundary Kit** owns native ABI and ownership contracts.
- **Wasm Component Kit** owns WIT/package/composition truth.
- **Schema Contract Kit** can supply structured type/data contracts where foreign surfaces depend on schemas.
- **Polyglot Productization Stack** imports Host Package as the foreign-consumer package/runtime anchor.
- **Extension Productization Stack** imports Host Package for install/update/package truth without flattening host/plugin or capability truth.
- **Web Productization Stack** can import JS/Wasm package identity and install truth without absorbing browser/runtime truth.
- **Release Truth Stack** attaches shipped artifacts and provenance.
- **Support Envelope Kit** owns support/runtime-floor/docs truth.
- **Debuggability Stack** can import tuple-specific debugging notes without becoming the package owner.

## Design principles
- **Keep crate identity separate from foreign package identity.**
- **Keep boundary truth separate from package truth.** Import `ffi-pack` or component facts; do not silently replace them.
- **Keep lanes comparable but non-equivalent.** Python wheels, Node addons, UniFFI outputs, headers/staticlibs, and Wasm components are not the same surface.
- **Make runtime assumptions explicit.** Threading, init, callback, async, ABI, interpreter/runtime, and SDK limits are part of the product surface.
- **Keep host-runtime guarantees lane-specific.** Node-API ABI stability, manylinux wheel compatibility, UniFFI threading rules, Python full-API vs `abi3` vs free-threaded vs `asyncio` bridge posture, and component/WIT guarantees are not interchangeable.
- **No fake universal binding model.** The kit standardizes review artifacts, not one blessed host-language abstraction.

## Evaluation plan
Pilot on five shapes:
1. PyO3 + maturin Python wheel
2. Node-API / `napi-rs` addon package
3. UniFFI Swift/Kotlin binding package
4. native handoff importing `ffi-pack`
5. Wasm component package importing component/WIT truth

## Success bar
- A downstream consumer can review what is being shipped to the host ecosystem without reading local packaging folklore.
- Runtime/support changes are distinguishable from pure boundary changes.
- Generated-binding provenance stays explicit.
- Package/install/docs/support consumers can import the result honestly.


## Python-specific sharpening
Read [`design/python-host-lane-map.md`](./python-host-lane-map.md) as the lane-splitting note beneath the generic `python` branch here.
For Python subjects, `cargo hostpkg` should keep **full-API extension**, **`abi3` limited-API extension**, **free-threaded extension**, **`asyncio` bridge**, and **embedding-adjacent notes** visibly distinct rather than collapsing them into one “PyO3 package” sentence.
