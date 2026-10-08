# Design: FFI Boundary Kit (`cargo ffi`, `ffi-pack/v0`)

## Goal
Make Rust↔C/C++ boundaries auditable, regenerable, diffable, and easier to integrate into non-Cargo build systems by defining:
- a reference CLI (`cargo ffi`),
- a portable boundary artifact (`ffi-pack/v0`),
- a machine-readable boundary manifest (`ffi-manifest/v0`),
- and release/CI reports for drift and breakage (`ffi-report/v0`).

## References (signals)
- Rust safety-critical vision: https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- C++/Rust interop problem map: https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- Rustonomicon FFI chapter: https://doc.rust-lang.org/nomicon/ffi.html
- Cargo build scripts: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- bindgen guide/requirements: https://rust-lang.github.io/rust-bindgen/ ; https://rust-lang.github.io/rust-bindgen/requirements.html
- cbindgen: https://github.com/mozilla/cbindgen
- autocxx: https://google.github.io/autocxx/
- Corrosion FFI binding integrations: https://corrosion-rs.github.io/corrosion/ffi_bindings.html

## Core UX: `cargo ffi`
- `cargo ffi inspect`
  - detect exported symbols, FFI modules, `repr(C)` types, `extern` surfaces, native links, generated header/binding inputs
- `cargo ffi generate`
  - generate or refresh boundary artifacts (headers, bindings, manifests)
- `cargo ffi verify`
  - check that generated outputs are in sync with sources and policy
- `cargo ffi diff <A> <B>`
  - compare two releases at the boundary level
- `cargo ffi pack`
  - emit `ffi-pack/v0` for downstream integrators and CI
- `cargo ffi doctor`
  - explain missing native libs, mismatched clang/header inputs, or build-system integration gaps

## Artifacts
### `ffi-manifest/v0`
- crate identity + version + toolchain
- directionality:
  - Rust exposes C ABI
  - Rust consumes C/C++ ABI
  - mixed / bi-directional
- exported items:
  - functions, opaque handles, repr(C) structs/enums, callbacks
- ownership contracts:
  - who allocates, who frees, lifetime notes, thread-safety notes
- generation inputs:
  - bindgen/cbindgen/autocxx/cxx config fingerprints
- native deps:
  - `links`, linker flags, pkg-config/vcpkg/framework expectations

### `ffi-pack/v0`
- `ffi-manifest.json`
- generated headers and/or bindings
- symbol snapshot
- boundary smoke tests or fixtures
- downstream integration notes (CMake/Meson/Bazel pointers)
- provenance: source revision, generator versions, toolchain tuple

### `ffi-report/v0`
- breakage classification:
  - added / removed / changed boundary items
  - layout/size/alignment drift where measurable
  - ownership contract changes
  - generator input drift
- severity hints:
  - likely source compatible / ABI risky / definitely breaking
- remediation hints:
  - regenerate bindings, update headers, rebuild native deps, pin toolchain

## Integration points
- `bindgen` / `cbindgen` / `cxx` / `autocxx` as generators, not competitors
- Cargo Report Kit for structured reports
- Public API Kit for release-boundary reasoning on the Rust side
- Cross Toolchain Kit for sysroot/clang/native toolchain inputs
- Safety Evidence Kit for audited boundary contracts in regulated environments

## Design principles
- Contract first, generator second.
- No promise of a stable Rust ABI; operate at explicit FFI surfaces only.
- Explainability over magic.
- Build-system neutrality: Cargo-native to produce, broadly consumable to ingest.

## Evaluation plan
- Pilot on three boundary shapes:
  - Rust library exposing a C ABI,
  - Rust crate binding to a C library with `bindgen`,
  - Rust ↔ C++ integration via `autocxx` or `cxx` plus CMake/Corrosion.
- Success bar:
  - CI can detect boundary drift before release.
  - A downstream C/C++ consumer can ingest the pack without reading the crate’s build script.


## Execution posture
- Treat this kit as the **boundary half** of a broader native-edge program, paired with [`design/native-dependency-kit.md`](./native-dependency-kit.md).
- The next credible execution move is a ranked pilot program rather than broad abstract standardization. See [`design/native-edge-pilot-program.md`](./native-edge-pilot-program.md).
- Start with C ABI export and bindgen/system-library lanes before richer C++ bridge and external-build-system handoff lanes.

## Pilot-specific success bar
- A downstream consumer can integrate the boundary without reading local generator folklore.
- Release drift is reason-coded and reviewable.
- Ownership contracts stay explicit instead of being inferred from headers or wrapper code.
- Native-provider expectations can attach cleanly without collapsing FFI truth into provider truth.
