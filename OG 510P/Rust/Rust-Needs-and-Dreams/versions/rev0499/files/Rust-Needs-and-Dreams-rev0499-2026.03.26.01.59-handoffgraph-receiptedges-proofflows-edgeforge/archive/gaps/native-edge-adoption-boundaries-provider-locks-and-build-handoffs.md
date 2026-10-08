## rev0415 addendum
The archive now promotes this gap into a first-class **Native Edge Contract** frontier.
Read it together with `design/native-edge-contract-2026Q1.md`: the gap is no longer only that Rust lacks nicer FFI helpers or nicer provider crates, but that it still lacks one portable review boundary above those non-equivalent lanes.


# Gap: native-edge adoption still lacks a portable boundary above FFI surfaces, native providers, and external build handoffs

## What is missing
Rust now has credible ingredients for mixed-language and native-library adoption, but it still lacks the **portable boundary that lets teams review one native-edge subject instead of reverse-engineering three different stories**.

Today the real adoption surface is usually split across:
- an FFI lane (`bindgen`, `cbindgen`, `cxx`, `autocxx`, handwritten `extern` blocks, generated headers/bindings),
- a native-provider lane (`pkg-config`, `system-deps`, `vcpkg`, `cmake`, vendored builds, Cargo artifacts, external build-system injection),
- and a build-handoff lane (Cargo-only success, CMake/Bazel/Buck/Nix/distro integration, release packaging, support/audit notes).

Those lanes are individually real, but the ecosystem still lacks one thin contract that can answer:
- what the Rust↔native boundary actually is,
- which native providers and link plans actually won,
- what host-vs-target/toolchain assumptions shaped the result,
- what generated artifacts belong to which source/toolchain inputs,
- what an external build system or downstream consumer is expected to ingest,
- and what release/support/audit consumers may safely conclude.

The missing contribution is therefore **not** another binding generator, another `-sys` helper, another CMake bridge, or another universal native package manager.
It is the **boring review boundary above the non-equivalent lanes**.

## Why this now matters
The current ecosystem signals are stronger than the archive’s older substrate-only framing:
- the 2025H1 Rust project goal **Evaluate approaches for seamless interop between C++ and Rust** was accepted specifically to enable Rust adoption in projects that must use large, rich C++ APIs;
- the 2025H2 **C++/Rust Interop Problem Space Mapping** effort says there are billions of lines of C++ and that external libraries currently solve the space in different ways, each requiring significant end-user investment;
- the July 2025 project-goals update says the language team established that Rust should evolve toward a **first-class C++ interop story**, while also stressing that interop needs are diverse rather than reducible to one tool;
- Cargo’s roadmap issue to **reduce the need for users to write build scripts** says build scripts cost build time, raise bug risk, and enlarge dependency-review scope, explicitly naming `-sys` / FFI territory as a lingering reason they persist;
- the sandboxed build-script goal says native dependency probing is one of the hardest reasons build scripts remain difficult to tame, which means native-provider truth is strategically important rather than merely annoying;
- Cargo’s build-script/reference docs say `links` metadata is real but still requires a build script, allows at most one package per `links` value, and passes metadata only to immediate dependents;
- the ecosystem’s point tools are visibly plural rather than converged: `system-deps` makes system-library requirements declarative in `Cargo.toml`; `pkg-config` shells out to the system utility in build scripts; CXX deliberately carves out a safe regime of Rust/C++ commonality; and `autocxx` explicitly targets large existing C++ codebases by combining automation with CXX-style safety.

Together these signals say the missing move is no longer just “improve one side of native interop.”
It is to make **native-edge adoption legible as one reviewed subject with linked but distinct boundary/provider/handoff truths**.

## What “good” looks like
A worthy contribution here is a thin stack that:
1. keeps **FFI boundary truth** separate from **native-provider/link truth**;
2. keeps **host/target/toolchain context** separate from both of those;
3. adds a clean **external-build / downstream-handoff** lane instead of assuming Cargo is the only consumer;
4. produces diffable artifacts that release/support/audit tooling can import;
5. composes with existing tools instead of pretending one bridge/provider lane has already won.

In archive terms, that means promoting an explicit **Native Edge Stack** above the existing FFI Boundary Kit and Native Dependency Kit, with a thin aggregate artifact such as `native-edge-pack/v0` that references lower-layer packs instead of erasing them.

## Distinction from nearby archive entries
- **FFI Boundary Kit** owns ABI-facing boundary manifests, generated artifacts, and boundary drift.
- **Native Dependency Kit** owns provider intent, provider locks, link plans, and reason-coded reports.
- **Polyglot Productization Stack** owns crate-vs-foreign-package identity, binding/package/runtime/support truth for shipped mixed-language products.
- **Native Edge Stack** should own the **adoption / build-handoff seam** that joins FFI boundary truth and native-provider truth into one reviewable subject for large mixed-language codebases and external build systems.

## Sources
- https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- https://github.com/rust-lang/rust-project-goals/blob/main/src/2025h2/interop-problem-map.md
- https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- https://github.com/rust-lang/cargo/issues/14948
- https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://docs.rs/system-deps/
- https://docs.rs/pkg-config
- https://cxx.rs/
- https://google.github.io/autocxx/
