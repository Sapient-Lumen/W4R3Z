# Design: Build Cache lane map (Cargo-native build-state, editor-private duplication, user-wide intermediates, wrapper caches, container layers, and CI exchange)

## Goal
Sharpen **Build Cache Kit** so the archive stops treating “Rust build cache” as one bucket.
The live ecosystem already spans materially different cache lanes, and they differ in **what subject is being cached**, **which directory topology and lock scope apply**, **whether reuse is Cargo-native or wrapper-defined**, **whether artifacts are intermediate or final**, **what policy intentionally duplicates work**, and **what downstream build/perf/support tooling may honestly conclude**.

The archive should therefore keep build-cache review grounded in a lane map instead of one flattened “cache hit or miss” story.

## Signals from the current ecosystem
- The Cargo Book now documents both `target-dir` and `build-dir`, explicitly says Cargo stores output in those directories, and distinguishes final artifacts from intermediate artifacts. It also still points users at `sccache` as a third-party shared-cache lane rather than treating it as built into Cargo.
  https://doc.rust-lang.org/cargo/reference/build-cache.html
- The 2025H2 Cargo goal for **Rework Cargo Build Dir Layout** says the current build cache is not easily broken into smaller units, that Cargo therefore locks the entire build cache, that this is felt when Rust Analyzer and CLI builds contend, and that the shiny future includes smaller cacheable/lockable units, a first-class user-wide cache, and plugin-based read/write to different cache sources.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The accepted **User-wide build cache** goal says today’s cache is per-workspace by default, that sharing `CARGO_TARGET_DIR` causes cross-project conflicts and `cargo clean` blast radius, and that the plan is to add user-wide caching for immutable non-local intermediate artifacts.
  https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
- The Cargo 1.94 cycle says target-dir locking still has tricky cases because locks must be held while reading fingerprints, and it explicitly calls out remaining contention around proc-macros and build scripts even after narrowing lock scope.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The March 13, 2026 call for testing says that with Cargo 1.91 users can already separate `build-dir` from `target-dir`, asks people to test `-Zbuild-dir-new-layout`, and documents ecosystem failure modes from tools that infer paths or scrape `OUT_DIR` / build-dir details.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo’s unstable docs say `fine-grain-locking` uses finer-grained locking instead of locking the entire build cache and note that it implicitly enables `build-dir-new-layout`.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- rust-analyzer’s `cargo.targetDir` setting is explicit that a rust-analyzer-specific target directory avoids locking contention at the expense of duplicating build artifacts.
  https://rust-analyzer.github.io/book/configuration.html
- `sccache`’s Rust docs are explicit that Rust support is focused on caching rustc invocations as produced by Cargo, that it has caveats, and that proc-macros reading files from the filesystem may not cache properly.
  https://github.com/mozilla/sccache/blob/main/docs/Rust.md
- `cargo-chef` is explicit that it is primarily for container builds, not normal local runs, that it splits `prepare` and `cook`, and that the same Rust version must be used in all stages for caching to work as expected.
  https://docs.rs/crate/cargo-chef/latest

## The lanes

### 1) Cargo-native workspace-local lane (`target-dir` / `build-dir` in one workspace)
This is the baseline lane for ordinary Cargo builds inside one workspace.

What defines it:
- Cargo-owned build-state layout
- final artifacts and intermediate artifacts living in related but separable directories
- Cargo fingerprinting and lock scope
- workspace-local reuse by default

Why it deserves its own lane:
- it is the baseline every other lane extends, avoids, or imports
- build-dir versus target-dir separation is now public enough to matter
- final-artifact visibility and intermediate-artifact reuse are not the same truth

Design rule:
- keep workspace-local Cargo-native build state separate from every wrapper/import lane layered above it

### 2) Editor-private coexistence lane (rust-analyzer or equivalent private target/build dir)
This is the lane where an editor duplicates build state on purpose to reduce contention with ordinary CLI builds.

What defines it:
- dedicated editor target/build directory or subdirectory
- deliberate duplication-by-policy
- different contention behavior from shared workspace-local state
- incomplete comparability with normal CLI cache statistics

Why it deserves its own lane:
- duplication is not a cache miss
- private editor state is a workflow policy decision, not a build failure
- this lane is strategically important for inner-loop experience even when it is less storage-efficient

Design rule:
- keep editor-private duplication separate from Cargo-native reuse verdicts and separate from future user-wide caching claims

### 3) Cargo-native user-wide immutable-intermediate lane
This is the lane Cargo is explicitly aiming toward for cross-workspace reuse of immutable, non-local intermediate artifacts.

What defines it:
- cross-workspace scope
- immutable intermediate-artifact reuse, not arbitrary final-artifact sharing
- stronger input hashing and entry identity
- Cargo-native lookup/write behavior rather than wrapper-owned semantics

Why it deserves its own lane:
- it is not the same as sharing one `CARGO_TARGET_DIR`
- it is not the same as compiler-wrapper caching
- it is one of the clearest emerging upstream landing zones in the ecosystem

Design rule:
- keep Cargo-native user-wide reuse separate from ad hoc shared-target-dir hacks and separate from remote/blob exchange claims

### 4) Compiler-wrapper cache lane (`RUSTC_WRAPPER=sccache` and adjacent wrappers)
This is the lane where Cargo still drives the build but a compiler wrapper decides whether a rustc invocation may be reused.

What defines it:
- wrapper-owned cache keys and storage
- rustc-invocation granularity rather than Cargo unit granularity
- caveats around supported arguments and tracked inputs
- possible local, shared, or remote backing stores

Why it deserves its own lane:
- it is real and useful, but it is not Cargo-native build-state truth
- wrapper reuse semantics differ from Cargo’s own future user-wide design
- proc-macro and filesystem-input caveats materially affect what can be claimed

Design rule:
- keep wrapper cache posture separate from Cargo-native build-state identity, lock scope, and reuse verdicts

### 5) Container recipe/layer lane (`cargo-chef` and analogous dependency-layer caching)
This is the lane where cache reuse is achieved by stabilizing a container build layer rather than by reusing Cargo-native build entries directly.

What defines it:
- recipe extraction (`prepare`) and dependency-layer replay (`cook`)
- container stage identity and Rust-toolchain consistency requirements
- cache keyed by container-layer invalidation semantics
- emphasis on dependency build reuse before application sources are copied

Why it deserves its own lane:
- a Docker layer cache is not a Cargo cache entry
- recipe stability and layer reuse tell a different story than rustc-unit reuse
- this lane is strategically important for production build pipelines even though it is not the right answer for local interactive builds

Design rule:
- keep container recipe/layer caching separate from Cargo-native reuse and separate from compiler-wrapper semantics

### 6) CI / plugin exchange lane (future Cargo plugins, coarse blob caches, selective remote exchange)
This is the lane where build state moves between machines or jobs.

What defines it:
- upload/download or read/write exchange policy
- full-blob versus entry-aware transfer behavior
- trust and source-of-truth posture for remote cache material
- explicit partiality when only imported cache evidence survives

Why it deserves its own lane:
- the build-dir-layout goal explicitly points toward plugin-based read/write and selective CI exchange
- coarse CI tarball restore is not the same thing as entry-aware build-state reuse
- this lane is where bandwidth, storage, and trust questions become first-class

Design rule:
- keep CI/plugin exchange separate from local cache identity and separate from wrapper-specific storage claims

## Lane transitions the archive must keep explicit
1. **workspace-local Cargo state ↔ editor-private duplication**
   - contention avoidance is not the same truth as reuse success.
2. **shared `CARGO_TARGET_DIR` folklore ↔ user-wide immutable-intermediate design**
   - one hacky shared directory is not the same thing as Cargo-native cross-workspace caching.
3. **Cargo-native unit reuse ↔ compiler-wrapper invocation reuse**
   - `sccache` hits are not the same thing as Cargo-native build-unit hits.
4. **Cargo/build-state reuse ↔ container recipe/layer reuse**
   - Docker layer stability is not proof that individual rustc work units would have reused.
5. **local entry existence ↔ remote exchange success**
   - blob restore/download success is not the same truth as actual entry reuse or safe write-back.
6. **intermediate-artifact reuse ↔ final-artifact publication**
   - build cache should not silently become artifact-selection or release-distribution truth.

## What should change elsewhere in the archive
- **Build Cache Kit** should remain the base artifact family, but it should now cite this lane map as the rule for what must stay separate.
- **Build-State Evidence Stack** should keep composing build-cache truth with change-impact and build-doctor imports instead of letting one layer overwrite the others.
- **Toolchain Productization** should keep owning sysroot/toolchain/runtime-family identity rather than letting cache reuse imply toolchain sameness.
- **Semantic Context / Edit Workflow** should import build-state facts rather than scraping build-dir details directly.
- **Perf / resource / support consumers** should import bounded cache-lane facts instead of retroactively inventing one cleaner cache story than the evidence supports.
