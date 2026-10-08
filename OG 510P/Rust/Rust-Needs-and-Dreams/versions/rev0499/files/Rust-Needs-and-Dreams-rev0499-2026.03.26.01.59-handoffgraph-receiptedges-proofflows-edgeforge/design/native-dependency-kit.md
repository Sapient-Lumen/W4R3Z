# Design: Native Dependency Kit (`cargo native`, `native-pack/v0`)

## Goal
Define a small, versioned substrate for **declaring native dependency intent, resolving provider choices, and emitting reviewable native link reports** so Rust projects can stop treating non-Rust dependencies as mostly opaque `build.rs` side effects.

This should not replace system package managers, vcpkg, CMake, distro packaging, Bazel/Nix/Buck rules, or Cargo artifact dependencies. It should give them a shared contract surface.

## References (signals)
- Cargo roadmap issue: reducing build-script reliance is now an explicit priority because build scripts hurt build time, bug risk, and audit scope.
  https://github.com/rust-lang/cargo/issues/14948
- RFC 2136: native dependencies are a specific cross-cutting concern for build-system interop, and existing `-sys` crates hide too much of that story inside custom build scripts.
  https://rust-lang.github.io/rfcs/2136-build-systems.html
- RFC 2196: declarative build scripts exist partly because broader systems need structured information about native dependencies now buried in `build.rs`.
  https://rust-lang.github.io/rfcs/2196-metabuild.html
- Sandboxed build scripts goal: determinism and least privilege are long-term Cargo goals, and native dependency probing is one of the trickiest remaining reasons arbitrary build scripts persist.
  https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- Cargo `links`: useful current primitive for native library identity + metadata passing, but still centered on build scripts and immediate-dependent metadata handoff.
  https://doc.rust-lang.org/cargo/reference/build-scripts.html
  https://doc.rust-lang.org/cargo/reference/manifest.html
- Cargo FAQ: duplicate `links` values still surface as concrete graph conflicts users must resolve manually.
  https://doc.rust-lang.org/beta/cargo/faq.html
- Existing provider crates show the ecosystem shape today:
  - `system-deps` declarative metadata over system libraries,
  - `pkg-config` provider shell-out,
  - `vcpkg` provider discovery,
  - `cmake` native-library build orchestration,
  - artifact dependencies for Cargo-built binaries/C-ABI outputs.
  https://docs.rs/system-deps/latest/system_deps/
  https://docs.rs/pkg-config/latest/pkg_config/
  https://docs.rs/crate/vcpkg/latest
  https://docs.rs/cmake/latest/cmake/
  https://rust-lang.github.io/rfcs/3028-cargo-binary-dependencies.html

## Core components

### 1) `native-intent/v0`
Canonical declaration of what a package needs from the non-Rust world.

Fields:
- package identity
- dependency items:
  - libraries
  - headers
  - tools / generators
  - frameworks / SDK packages
- role:
  - `build-host`
  - `compile-target`
  - `both`
- provider preferences:
  - `pkg-config`
  - `system-deps`
  - `vcpkg`
  - `cmake-package`
  - `vendored-build`
  - `cargo-artifact`
  - `external-build-system`
  - `manual-config`
- version / capability constraints
- static/dynamic preference
- optional feature gating
- optional fallback order

Design rule: v0 is about **declared intent**, not observed results.

### 2) `native-provider-lock/v0`
The resolved provider decision for one build context.

Fields:
- package identity
- target triple and host triple
- provider chosen per native item
- exact resolved version/package identifier where available
- source provenance:
  - package-manager coordinate
  - path / sysroot / SDK identifier
  - Cargo artifact reference
  - external build-system reference
- key config and env inputs that affected resolution
- freshness / reproducibility notes

Design rule: the lock must explain **which provider won and why**, not just record a filesystem path.

### 3) `native-link-plan/v0`
A normalized account of what must happen for the Rust build to link successfully.

Fields:
- include directories
- library search paths
- linked libraries / frameworks
- defines / compile flags passed to generated native compilations
- tools invoked (`pkg-config`, `cmake`, compiler wrappers, generators)
- generated outputs consumed by Rust code or downstream native builds
- fallback notes and warnings

Design rule: this is not a replacement for raw build logs; it is the diffable, machine-readable summary.

### 4) `native-report/v0`
A session-level report for one actual resolution/build invocation.

Fields:
- inputs:
  - manifest metadata
  - active features
  - target(s)
  - relevant config paths
- resolved provider locks
- link plan
- reason codes:
  - `MISSING_PROVIDER`
  - `VERSION_CONFLICT`
  - `DUPLICATE_LINKS_VALUE`
  - `HOST_TARGET_CONFUSION`
  - `VENDORED_FALLBACK_USED`
  - `MANUAL_OVERRIDE_APPLIED`
  - `NONDETERMINISTIC_PROBE`
- timings / probe summaries
- raw attachment references if needed

Design rule: make the report useful for CI, bug reports, and build-system bridges without forcing consumers to parse stdout.

### 5) `native-pack/v0`
Portable bundle carrying:
- `native-intent/v0`
- `native-provider-lock/v0`
- `native-link-plan/v0`
- `native-report/v0`
- optional raw attachments:
  - `pkg-config` output
  - CMake cache fragments
  - provider manifests
  - generated config headers

Design rule: attach raw material when needed, but keep the summary schemas first-class.

### 6) `cargo native`
Reference UX:
- `cargo native inspect` — infer and summarize current native intent
- `cargo native lock` — emit `native-provider-lock/v0`
- `cargo native plan` — emit `native-link-plan/v0`
- `cargo native report` — emit `native-report/v0`
- `cargo native doctor` — explain missing/conflicting providers or duplicate `links`
- `cargo native pack` — bundle `native-pack/v0`

Design rule: start as an adapter over existing Cargo/build-script/provider behavior rather than demanding a single new native package manager.

## What the kit should provide to others
- **`-sys` and mixed-language crates:** one place to express and report native needs without burying everything in ad hoc probing logic.
- **External build systems:** a structured handoff surface for supplying approved native deps instead of reverse-engineering `build.rs` behavior.
- **Cross-compilation workflows:** a cleaner separation between “which toolchain do I have?” and “which native libraries/providers satisfy this build?”
- **Reproducibility and policy tooling:** attachable provider locks and reason codes.
- **FFI and release tooling:** a reviewable native-dependency layer that can travel with headers, bindings, artifacts, and attestations.

## Hard problems (explicitly scoped)
1. **Do not flatten provider diversity**
   - `pkg-config`, `vcpkg`, vendored source builds, and Cargo artifact dependencies are different lanes with different trust and portability properties.
2. **Host vs target must stay explicit**
   - native generators and link targets often differ, especially in cross builds.
3. **System paths are not enough**
   - a lock that only records `/usr/lib/libssl.so` is not an adequate explanation.
4. **Build scripts remain for a while**
   - v0 must work as an adapter around existing `build.rs` ecosystems, not assume instant migration.
5. **Distro and org integration matters**
   - external build systems need to inject native providers without being forced to mimic Cargo internals.

## Overlap boundaries
- **Build Extension Kit** may consume `native-intent/v0` for declarative steps, but it does not own provider locking.
- **Build Interop Kit** may carry `native-report/v0` as part of larger build plans, but it does not define the native schemas.
- **Cross Toolchain Kit** prepares compilers, SDKs, and sysroots; Native Dependency Kit resolves libraries/tools on top of that foundation.
- **FFI Boundary Kit** uses native provider facts as attachments, but keeps ABI/bindings contracts separate.
- **Compile-Time Capabilities Kit** governs what native discovery/build steps are permitted.
- **Repro Build Kit** consumes `native-provider-lock/v0` and `native-report/v0` instead of trying to reconstruct them after the fact.

## Evaluation plan
Pilot on:
1. a classic `pkg-config`-based `-sys` crate,
2. a crate using `system-deps` metadata,
3. a Windows-targeting crate using `vcpkg`,
4. a vendored-source build via `cmake`,
5. one mixed Cargo + external-build-system integration.

Success bar:
- provider choices become explainable and diffable,
- duplicate `links` / fallback behavior become easier to diagnose,
- external build systems gain a cleaner override surface,
- and adjacent kits can consume native facts without absorbing native dependency management wholesale.


## Execution posture
- Treat this kit as the **provider / link-plan half** of a broader native-edge program, paired with [`design/ffi-boundary-kit.md`](./ffi-boundary-kit.md).
- The next credible move is a ranked pilot program across system-library consumers, C++ bridge lanes, and external build handoff flows. See [`design/native-edge-pilot-program.md`](./native-edge-pilot-program.md).
- Start as an adapter around existing provider crates and Cargo behavior. The goal is to make their choices portable and explainable, not to replace them all.

## Pilot-specific success bar
- `-sys` and mixed-language crates can explain provider choice and link plans without dumping raw stdout into issues.
- host/target confusion, duplicate `links`, and vendored fallbacks get reason-coded reports.
- external build systems gain a cleaner override/injection seam.
- adjacent kits can consume native facts without absorbing native dependency management wholesale.
