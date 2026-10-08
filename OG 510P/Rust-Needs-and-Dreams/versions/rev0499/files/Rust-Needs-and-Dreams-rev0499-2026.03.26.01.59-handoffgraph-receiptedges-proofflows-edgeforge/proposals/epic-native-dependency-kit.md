# Epic Proposal: Native Dependency Kit (`cargo native`, `native-pack/v0`)

## One-sentence pitch
Make Rust’s non-Rust dependencies first-class by standardizing native dependency intent, provider locks, link plans, and attachable reports so `-sys` crates and mixed-language builds stop relying on opaque build-script folklore as their main contract.

## Deliverables
- `cargo native` reference tool
- Schemas:
  - `native-intent/v0`
  - `native-provider-lock/v0`
  - `native-link-plan/v0`
  - `native-report/v0`
  - `native-pack/v0`
- Adapters / integrations for:
  - `system-deps`
  - `pkg-config`
  - `vcpkg`
  - `cmake`
  - Cargo artifact dependencies
  - external-build-system injection / override flows
- Docs:
  - provider taxonomy + capability model
  - host/target resolution rules
  - duplicate `links` conflict guidance
  - vendored vs system vs artifact-provider tradeoffs

## Why now (signals)
- Cargo now explicitly wants fewer user-authored build scripts because they cost build time, bug surface, and audit surface.
  https://github.com/rust-lang/cargo/issues/14948
- RFC 2136 and RFC 2196 both identify native dependencies as a key reason Cargo integration with larger build systems remains awkward.
  https://rust-lang.github.io/rfcs/2136-build-systems.html
  https://rust-lang.github.io/rfcs/2196-metabuild.html
- The sandboxed-build-script goal frames build-script determinism and least privilege as important ecosystem goals, which increases the value of moving native discovery facts into structured artifacts.
  https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- Cargo’s existing `links` mechanism and FAQ prove that native dependency identity/conflict handling is already a real graph-level concern, but still an under-modeled one.
  https://doc.rust-lang.org/cargo/reference/build-scripts.html
  https://doc.rust-lang.org/beta/cargo/faq.html
- The ecosystem already has serious point tools (`system-deps`, `pkg-config`, `vcpkg`, `cmake`) and an adjacent Cargo primitive (artifact dependencies), so the missing contribution is a convergence contract, not one more bespoke provider crate.
  https://docs.rs/system-deps/latest/system_deps/
  https://docs.rs/pkg-config/latest/pkg_config/
  https://docs.rs/crate/vcpkg/latest
  https://docs.rs/cmake/latest/cmake/
  https://rust-lang.github.io/rfcs/3028-cargo-binary-dependencies.html

## Non-goals
- A universal system package manager for Rust
- Replacing distro packaging, vcpkg, or CMake
- Promising that every `build.rs` can disappear immediately
- Flattening system, vendored, and artifact-based providers into one fake portability story
- Defining one canonical ABI/bindings format for FFI surfaces

## Strategic value
This is a worthy contribution because it closes a leverage-heavy seam that several other archive kits now depend on implicitly:
- **Build Extension Kit** needs a structured native-deps target rather than continuing to treat providers as opaque imperative behavior.
- **Cross Toolchain Kit** becomes more useful when it can hand off to a known native-provider contract.
- **FFI Boundary Kit** benefits when native library/provider expectations are attachable and diffable.
- **Repro Build Kit** gains a better basis for explaining why rebuilds diverged.
- **Build Interop Kit** gets a clearer bridge to external build systems and distro rules.
- **Compile-Time Capabilities Kit** gets a better story for what native discovery/build behavior can be reduced or sandboxed.

It also fits the archive’s larger strategy: prefer **shared artifacts and explainable contracts** over new mega-tools.

## Milestones
1. **v0 schemas + fixtures**
   - define `native-intent`, `native-provider-lock`, `native-link-plan`, `native-report`
   - publish examples spanning system/provider/vendored/artifact cases
2. **Provider adapters**
   - map current `system-deps`, `pkg-config`, `vcpkg`, and `cmake` behavior into the schemas
   - emit conflict and fallback reason codes
3. **Interop pilots**
   - external-build-system override / injection flow
   - CI / release attachments via `native-pack/v0`
4. **Cross-kit pilots**
   - attach to FFI, Repro Build, Cross Toolchain, and Build Extension workflows

## Success criteria
- ordinary `-sys` crates can express and report native dependency choices more clearly,
- build failures around providers and `links` become easier to diagnose,
- external build systems gain a cleaner supply/override seam,
- and the ecosystem gets a portable native-dependency artifact layer without pretending there is one blessed provider for every platform.

## Execution posture
- Execute this as part of the ranked native-edge pilot program in [`design/native-edge-pilot-program.md`](../design/native-edge-pilot-program.md), starting with system-library consumer lanes before broader external-build handoff and audited adoption lanes.
- Position this as a companion evidence substrate to Cargo's build-script / artifact-dependency direction, not as a new universal package manager.
