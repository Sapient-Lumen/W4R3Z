# Gap: Toolchain variants, sysroots, cross-builds, and sanitizer-support contracts

> rev0412 note: read this gap through the new contract boundary in `design/toolchain-productization-contract-2026Q1.md` so provisioning, sysroot/profile identity, activation/reuse, runtime-analysis, support posture, and downstream handoff do not collapse into one fake custom-toolchain story.

## The gap
Rust increasingly needs to ship and consume **toolchain variants as products**, not just as whatever happened to be installed on one developer laptop.

The official signals now say this pretty clearly:
- the `build-std` goal is about a minimum viable design that could plausibly be stabilized, not a forever-experimental `-Z` escape hatch;
- Cargo’s unstable docs still describe `-Z build-std` as early-stage and require nightly plus `rust-src` plus passing the flag to every invocation;
- rustup still treats toolchains, components, targets, profiles, and directory overrides as separate control surfaces;
- custom targets explicitly warn that target JSON is unstable and should be pinned to a compiler version;
- the sanitizer-support goal says MemorySanitizer and ThreadSanitizer need infrastructure for **precompiled and instrumented standard libraries**, and the 2026 flagships page carries that work forward;
- Rust for Linux needs stable foundations for custom std/core builds plus ABI-affecting, hardening, and sanitizer-related compiler options;
- the end-of-2025 program update says adopters like CPython are surfacing a very similar cluster of needs.

Taken together, the missing problem is no longer “can somebody hack this together with rustup, nightly, and CI glue?”
The missing problem is:

**how do Rust teams name, provision, activate, cache, transport, diff, and trust the exact toolchain variant they are actually building and testing with?**

## What is missing
The ecosystem still lacks a portable layer that keeps these truths distinct but composable. [`design/toolchain-productization-lane-map.md`](../design/toolchain-productization-lane-map.md) is now the archive rule for keeping the lane families separate instead of narrating one fake custom-toolchain story:

1. **Provisioning truth**
   - rustup channel/toolchain identity
   - component/profile/target installation posture
   - external linker/SDK/sysroot/C toolchain acquisition
   - local-vs-archived-vs-linked custom toolchain origin

2. **Stdlib / sysroot truth**
   - which std/core/alloc/proc_macro/test crates were rebuilt
   - with what source revision, compiler, custom target, and codegen knobs
   - whether the profile was baseline, hardened, instrumented, core-only, or custom-target specific

3. **Activation truth**
   - how a workspace or external build selected the toolchain/sysroot
   - rustup override or `rust-toolchain.toml` posture
   - Cargo config / linker / target selection
   - reuse rules, compatibility bounds, and mismatch rejection reasons

4. **Runtime-analysis / hardening truth**
   - whether std itself was instrumented
   - what sanitizer or mitigation lane actually ran
   - what runtime libraries, cross-language flags, or platform limits applied
   - what findings are comparable versus lane-specific

5. **Consumer import truth**
   - what firmware, release, safety, CI, support, and incident consumers may conclude
   - what remains local, unstable, best-effort, or unsupported

## What this should not become
This should **not** become:
- another wrapper around `-Z build-std`;
- another cross-compilation convenience frontend;
- a universal replacement for rustup;
- one more org-local cache format dressed up as an ecosystem standard;
- a release-provenance system that swallows runtime-analysis truth;
- a fake “custom toolchain works” badge.

The missing contribution is a **reviewable toolchain-as-product boundary** above the existing ingredients.

## What a worthy contribution would look like
A real contribution here would define a thin artifact family and workflow that can:
- import or emit provisioning facts (`toolchain-pack/v0`), stdlib facts (`sysroot-pack/v0`), activation facts (`sysroot-activation/v0`), and dynamic-analysis facts (`sanitize-pack/v0`);
- explain what exact compiler/std/target/profile family a build used;
- diff two toolchain variants without collapsing provisioning, stdlib identity, activation, and sanitizer evidence into one score;
- let tools answer questions like:
  - “which stdlib profile did this firmware or service binary actually use?”
  - “is this cache entry safely reusable for this custom target and mitigation profile?”
  - “did this sanitizer run use an instrumented stdlib, or only instrument local crates?”
  - “which parts came from rustup, which from local builds, and which from external SDKs or linkers?”
  - “what exactly changed when the toolchain or target profile changed?”

## Likely shape of the solution
The strongest path is an explicit **Toolchain Productization Stack** that composes:
- **Cross Toolchain Kit** for compiler/linker/SDK/provisioning truth;
- **Sysroot Pack Kit** for rebuilt std/core identity and transport;
- **Sanitizer Battery Kit** for runtime-analysis and instrumentation truth;
- optional imports from **Support Envelope**, **Release Truth**, **Safety-Critical Evidence**, and **Firmware Productization** when a consumer needs them.

This would let the ecosystem talk about **toolchain variants as products** instead of as hidden machine state, while preserving stock rustup, local build-std, reusable sysroot packs, compiler-pinned custom targets, activation policy, runtime-family claims, and external handoff as distinct lanes.

## Why this belongs in the archive now
The archive already had the right ingredients and even a pilot program.
What it did **not** yet have was the explicit synthesis saying that the next worthy contribution is likely **not** another lower-layer wrapper at all.
It is the layer that joins toolchain provisioning, stdlib variants, activation, and runtime-analysis evidence into one honest contract.

## References (signals)
- lane map companion:
  [`design/toolchain-productization-lane-map.md`](../design/toolchain-productization-lane-map.md)
- build-std goal:
  https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
- Cargo unstable `build-std` docs:
  https://doc.rust-lang.org/cargo/reference/unstable.html
- rustup toolchains:
  https://rust-lang.github.io/rustup/concepts/toolchains.html
- rustup components:
  https://rust-lang.github.io/rustup/concepts/components.html
- rustup cross compilation:
  https://rust-lang.github.io/rustup/cross-compilation.html
- rustup overrides / `rust-toolchain.toml`:
  https://rust-lang.github.io/rustup/overrides.html
- rustc custom targets:
  https://doc.rust-lang.org/rustc/targets/custom.html
- sanitizer support goal:
  https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- Rust in 2026 flagships:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- sanitizer docs:
  https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
- Rust for Linux tooling goal:
  https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- program management update — end of 2025:
  https://blog.rust-lang.org/inside-rust/2025/12/19/program-management-update--end-of-2025/
