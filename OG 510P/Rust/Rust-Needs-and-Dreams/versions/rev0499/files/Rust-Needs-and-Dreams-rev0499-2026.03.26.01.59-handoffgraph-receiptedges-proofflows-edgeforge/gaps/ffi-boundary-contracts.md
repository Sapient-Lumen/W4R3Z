# Gap: FFI boundary contracts and native-integration ergonomics

## Summary
Rust adoption often succeeds by joining an existing C or C++ world, not by replacing it. But today the Rust ecosystem still makes teams stitch together multiple partially-overlapping tools and conventions:
- `bindgen` for C/C++ → Rust bindings,
- `cbindgen` for Rust → C/C++ headers,
- `cxx` / `autocxx` for higher-level C++ interop,
- Cargo build scripts and `links` metadata for native libraries,
- build-system bridges like Corrosion for CMake-heavy environments.

These are useful pieces, but the boundary itself is still too implicit. Teams lack a portable, reviewable contract for:
- what symbols/types are exposed,
- which ownership and layout assumptions matter,
- which native libraries and toolchains are required,
- which generated headers/bindings correspond to which Rust release,
- and whether the boundary broke across a release.

## Ecosystem signals
- The Rust safety-critical vision explicitly says many teams will integrate Rust into existing C and C++ systems for years, and that guidance/tooling to keep interfaces correct, auditable, and in sync would help.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The 2025H2 project goal “C++/Rust Interop Problem Space Mapping” exists specifically to map the technical issues with broad community consensus.
  https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- The Rustonomicon still teaches FFI via C interfaces and says Rust cannot directly call into a C++ library.
  https://doc.rust-lang.org/nomicon/ffi.html
- `bindgen` relies on `libclang`, which is powerful but adds host/toolchain coupling.
  https://rust-lang.github.io/rust-bindgen/requirements.html
- `cbindgen` exists because hand-maintaining headers is error-prone.
  https://github.com/mozilla/cbindgen
- Cargo build scripts remain the mechanism for native linking and metadata handoff.
  https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Corrosion helps integrate Cargo with CMake, but FFI binding integrations are still a distinct concern.
  https://corrosion-rs.github.io/corrosion/ffi_bindings.html

## What “good” looks like
- A machine-readable boundary manifest that can be diffed in CI.
- Generated headers/bindings that are tied to exact source + toolchain inputs.
- Native dependency/toolchain requirements made explicit and exportable.
- Release-time ABI / API drift reports at the boundary.
- Build-system-friendly packs that downstream C/C++ consumers can ingest without reverse-engineering the Rust crate.
