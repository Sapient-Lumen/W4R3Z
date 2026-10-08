# Gap: native dependency resolution is still hidden behind provider-specific build-script folklore

## Summary
Rust has made real progress on Cargo plumbing, build-script reduction, sandboxing, artifact dependencies, and FFI review. But one practical seam still sits in an awkward middle:

**How does a crate declare, resolve, explain, and lock the non-Rust libraries, headers, tools, and provider choices it depends on?**

Today that answer is usually split across:
- `build.rs` logic,
- `links` keys and `DEP_*` metadata,
- environment-variable conventions,
- provider-specific helper crates,
- vendored fallbacks,
- distro/Bazel/Buck/Nix overrides,
- and README installation notes.

That works, but it is not a clean substrate for reproducibility, auditability, external build-system integration, or boring cross-platform support.

## Why now
- Cargo’s current roadmap explicitly says it wants to **reduce the need for users to write build scripts**, because build scripts hurt build times, increase bug risk, and enlarge dependency-review scope.
  https://github.com/rust-lang/cargo/issues/14948
- The build-systems RFC explicitly calls out **native dependencies** as a cross-cutting concern: existing `-sys` crates tend to manage them through custom build scripts, but external build systems want to provide and control those dependencies directly.
  https://rust-lang.github.io/rfcs/2136-build-systems.html
- RFC 2196 says the biggest problem for broader build-system integration is that `build.rs` hides information about native dependencies that other systems need in structured form.
  https://rust-lang.github.io/rfcs/2196-metabuild.html
- The sandboxed build-script goal says build scripts can do everything from network access to arbitrary binary execution, and frames determinism + least privilege as important long-term goals. Native dependency discovery is one of the main reasons those scripts remain hard to tame.
  https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- Cargo’s `links` mechanism helps, but it still requires a build script, allows only one package per `links` value, and passes metadata only to immediate dependents. That is a useful primitive, not a full dependency-resolution contract.
  https://doc.rust-lang.org/cargo/reference/build-scripts.html
  https://doc.rust-lang.org/beta/cargo/faq.html
- The ecosystem already has partially declarative pieces: `system-deps` moves system-library requirements into `Cargo.toml` metadata, while `pkg-config`, `vcpkg`, and `cmake` each document a different build-script-centered provider model. That is strong evidence of need, but also of fragmentation.
  https://docs.rs/system-deps/latest/system_deps/
  https://docs.rs/pkg-config/latest/pkg_config/
  https://docs.rs/crate/vcpkg/latest
  https://docs.rs/cmake/latest/cmake/
- RFC 3028 and Cargo’s unstable artifact dependencies let crates depend on Cargo-built binaries or C-ABI artifacts, which is an important adjacent primitive. But it does not solve the larger “which system/native provider satisfied this dependency, and why?” problem.
  https://rust-lang.github.io/rfcs/3028-cargo-binary-dependencies.html
  https://doc.rust-lang.org/beta/cargo/reference/unstable.html

## Concrete missing pieces
1. **Declarative native intent**
   - required libraries, headers, tools, frameworks, or SDK components
   - host vs target needs
   - acceptable providers and fallback order
   - static / dynamic / vendored preferences

2. **Provider-aware locks**
   - not just “found OpenSSL somehow”, but:
     - provider kind (`pkg-config`, `vcpkg`, `cmake-package`, vendored, Cargo artifact, external-build-system, manual)
     - exact version / package id / tool version where possible
     - target triplet and host/target role
     - provenance and freshness hints

3. **Reviewable link plans**
   - which include dirs, libs, frameworks, defines, and tool invocations were actually used
   - which environment variables or config knobs changed the result
   - why a fallback path activated

4. **Conflict explanation**
   - duplicate `links` collisions
   - incompatible provider choices across the graph
   - one crate assuming vendored OpenSSL while another assumes system OpenSSL
   - host/target confusion in cross builds

5. **A clean handoff to adjacent kits**
   - Cross Toolchain Kit should not have to guess which native libraries a build expects.
   - Repro Build Kit should not infer native provider choices from logs.
   - FFI Boundary Kit should not be the source of truth for native dependency resolution.
   - Build Extension Kit should not absorb provider locking just because `build.rs` currently does everything.

## Desired properties
- Expressive enough for real `-sys` crates and mixed-language workspaces.
- Honest about provider differences instead of flattening them into fake portability.
- Usable by Cargo-native builds and by external build systems.
- Capable of producing lockable, attachable artifacts for CI and releases.
- Narrow enough that v0 does not try to redesign every distro, package manager, or SDK story.

## Distinction from nearby archive entries
- **FFI Boundary Kit** describes ABI surfaces and generated headers/bindings. Native Dependency Kit describes how native libraries/tools are located, selected, built, and linked.
- **Build Extension Kit** is about declarative replacement for common `build.rs` steps and safe artifact uplift. Native Dependency Kit is about provider selection, locks, and link plans.
- **Cross Toolchain Kit** is about sysroots, linkers, SDKs, and target toolchain provisioning. Native Dependency Kit is about the libraries and tools the crate graph depends on once the toolchain exists.
- **Compile-Time Capabilities Kit** governs what build scripts may do. Native Dependency Kit reduces how much opaque discovery they need to do in the first place.
- **Repro Build Kit** verifies rebuild equivalence. Native Dependency Kit gives it a cleaner source for native-provider facts.
