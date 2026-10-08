# Design: Sysroot Pack Kit (`cargo sysroot`, `sysroot-pack/v0`)

## Goal
Define a portable workflow and artifact contract for **building, packaging, reusing, and auditing custom Rust standard-library sysroots**.

This should not replace Cargo’s eventual `build-std` design, rustup, distro packaging, or bespoke org caches.
It should give them a shared substrate.

## Strategic posture now
This kit should now be treated as the **anchor** of a broader toolchain-productization band:
- [`design/toolchain-productization-pilot-program.md`](./toolchain-productization-pilot-program.md)
- [`design/cross-toolchain-kit.md`](./cross-toolchain-kit.md)
- [`design/sanitizer-battery-kit.md`](./sanitizer-battery-kit.md)

The core archive decision is that the missing contribution is **not** “make `build-std` easier once on one laptop”.
It is “make custom, instrumented, hardened, or target-specific Rust stdlib builds portable enough to cache, activate, review, and reason about across real workflows.”

Read this together with [`design/toolchain-productization-lane-map.md`](./toolchain-productization-lane-map.md): Sysroot Pack is the reusable-stdlib lane, not the whole toolchain story. Stock rustup provisioning, host/target activation, custom-target coupling, and instrumented-runtime-family claims must remain distinct imported truths.

## References (signals)
- The build-std goal is now explicitly about an MVP that could be stabilized, and it calls out the need to make standard-library sources available, build them without nightly-only workflow assumptions, and tell the compiler to use the resulting rebuilt libraries in a standard way.
  https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
- The October 2025 program update says build-std RFCs were posted, including “always” and “explicit dependencies”, which is a much stronger maturity signal than the old experimental state.
  https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/
- Cargo’s current unstable docs still show the friction points: nightly toolchain, `rust-src`, and `-Z build-std` passed to every cargo invocation.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Rust for Linux needs custom std/core builds plus stable foundations for ABI-affecting flags, hardening, and tooling workflows; the end-of-2025 program update also says similar needs are showing up in CPython exploration.
  https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
  https://blog.rust-lang.org/inside-rust/2025/12/19/program-management-update--end-of-2025/
- Rust’s sanitizer docs already recommend rebuilding and instrumenting std for some workflows, and the 2026 sanitizer-support flagship explicitly calls out the need to provide **precompiled and instrumented standard libraries**. That makes “instrumented stdlib identity” a real ecosystem concern rather than a hypothetical one.
  https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
  https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- Custom target workflows still point users at build-std and explicitly warn that target JSON and compiler version must be pinned together.
  https://doc.rust-lang.org/rustc/targets/custom.html

## Core components

### 1) `sysroot-intent/v0`
Declares what rebuilt standard library is wanted.

Fields:
- compiler identity:
  - rustc version/channel/commit hash where available
  - Cargo version
- source provenance:
  - `rust-src` or alternate std source revision identifier
- build scope:
  - `core`
  - `alloc`
  - `std`
  - `proc_macro`
  - `test`
- target identity:
  - target triple or custom-target file identity/hash
- profile and codegen knobs:
  - opt level
  - debug assertions
  - panic strategy
  - LTO / codegen options
- profile family:
  - `baseline`
  - `instrumented`
  - `hardened`
  - `custom-target`
  - `core-only`
  - `size-tuned`
- specialization knobs:
  - target features / CPU
  - hardening / mitigation flags
  - sanitizer/instrumentation expectations
  - selected cfgs that affect std shape
- motivation tags:
  - `tier3-target`
  - `embedded-size`
  - `instrumented-stdlib`
  - `kernel/core-only`
  - `custom-abi`
  - `repro-build`

Design rule: v0 records the **requested std rebuild**, not the observed artifacts.

### 2) `sysroot-pack/v0`
Portable manifest for one built custom sysroot.

Fields:
- embedded or attached `sysroot-intent/v0`
- build host identity
- exact build inputs used
- output artifact list with hashes:
  - rlibs / dylibs / metadata where applicable
  - docs/json attachments if present
- compatibility notes:
  - required compiler range or exact compiler identity
  - target/custom-target compatibility
- pack layout version
- optional signatures / attestations references

Design rule: a sysroot pack must be enough to move or cache the rebuilt std artifacts without guessing which flags created them.

### 3) `sysroot-activation/v0`
How a consumer workspace or external build system selects and uses a sysroot pack.

Fields:
- pack identity/hash
- expected compiler/toolchain identity
- activation mode:
  - Cargo-managed
  - rustc-direct
  - external-build-system handoff
- selected standard crates from the pack
- mismatch policy:
  - warn
  - fail
  - permit if compatible-range matches

Design rule: keep “I built it” separate from “I am now using it”.

### 4) `sysroot-report/v0`
Session-level report for an actual sysroot build or reuse event.

Fields:
- inputs and effective configuration
- whether build happened or cached pack was reused
- timings / cache hit summaries
- warnings and reason codes:
  - `MISSING_RUST_SRC`
  - `NIGHTLY_REQUIRED`
  - `TARGET_SPEC_MISMATCH`
  - `TOOLCHAIN_MISMATCH`
  - `UNSUPPORTED_STD_SCOPE`
  - `INSTRUMENTATION_REQUIRES_REBUILD`
  - `ACTIVATION_REJECTED`
- produced or consumed pack identities
- optional raw attachments:
  - cargo/rustc logs
  - target JSON
  - rustup component inventory

Design rule: make sysroot reuse explainable in CI instead of leaving teams to infer it from target directory state.

### 5) `cargo sysroot`
Reference UX:
- `cargo sysroot plan` — resolve std scope + inputs, emit `sysroot-intent/v0`
- `cargo sysroot build` — build or rebuild the sysroot
- `cargo sysroot pack` — emit `sysroot-pack/v0`
- `cargo sysroot activate` — emit `sysroot-activation/v0` and configure local use
- `cargo sysroot report` — emit `sysroot-report/v0`
- `cargo sysroot doctor` — explain why a requested custom std build is unavailable or unsafe to reuse

Design rule: start as a layer *over* Cargo/rustc/rustup realities rather than waiting for every upstream stabilization detail to finish.

## What the kit should provide to others
- **Cross-compilation / custom-target users:** reusable and explainable std/core builds instead of rebuilding ad hoc or depending on hidden cache state.
- **Rust-for-Linux and low-level consumers:** a clearer path to “build core yourself” workflows with portable evidence.
- **Sanitizer / exploit-mitigation workflows:** one place to record whether std itself was instrumented.
- **Reproducibility and release tooling:** stable attachment points for sysroot identity rather than baking target-dir folklore into provenance reports.
- **Org caches / remote execution:** deterministic pack keys and explicit compatibility rules.

## Hard problems (explicitly scoped)
1. **Do not redefine build-std itself**
   - Upstream Cargo owns the blessed build mechanism.
   - This kit owns packaging, activation, reporting, and reuse contracts around that mechanism.
2. **Custom targets must remain explicit**
   - Target JSON is unstable and compiler-version-coupled; the pack must capture that honestly.
3. **Instrumented stdlib is not generic stdlib**
   - CFI/CFG/sanitizer/hardening configurations change compatibility expectations and must be first-class metadata.
4. **Cargo and non-Cargo builders both matter**
   - Rust-for-Linux-style `build-core` needs should not be excluded just because Cargo is the dominant UX.
5. **Reuse must be policyable**
   - “Looks close enough” is not a sufficient activation story for safety/security-sensitive builds.

## Overlap boundaries
- **Cross Toolchain Kit** provisions compilers, SDKs, and generic sysroots; Sysroot Pack Kit defines the identity and transport of rebuilt Rust std artifacts.
- **Build Extension Kit** may reference sysroot packs as inputs or outputs, but does not define their manifest or activation semantics.
- **Sanitizer Battery Kit** records runtime-checking profiles/results and consumes sysroot facts when std itself is instrumented.
- **Repro Build Kit** consumes `sysroot-pack/v0` and `sysroot-report/v0` as inputs to rebuild verdicts.
- **Formal Verification Kit** may attach proof assumptions about std provenance, but does not own sysroot build metadata.
- **Native Dependency Kit** is about non-Rust libraries/tools, not the Rust standard library itself.

## Evaluation plan
Use [`design/toolchain-productization-pilot-program.md`](./toolchain-productization-pilot-program.md) as the ranked execution layer.

The short version:
1. instrumented-stdlib lane,
2. hardened / ABI-modifying lane,
3. custom-target / tier-3 lane,
4. shared-cache / CI lane,
5. external-build-system handoff lane.

Success bar:
- teams can explain *which* stdlib they are linking,
- instrumented or hardened std builds stop hiding in local state,
- cache reuse becomes deliberate instead of folkloric,
- adjacent kits stop duplicating sysroot identity fields,
- and upstream build-std work gains a natural ecosystem-grade attachment point.
