## Execution note (rev0448)
Read this note now as the contract substrate beneath `design/toolchain-productization-execution-blueprint-2026Q1.md`.
The sharper answer is no longer only “toolchain/sysroot/sanitizer concerns belong together”, but “the worthy contribution should ship a **reference layer + report/pack command + profile/acceptance corpus** that keeps provisioning, sysroot, activation, runtime-lane, support-envelope, and consumer-handoff truth separate.”

# Design: Toolchain Productization Contract 2026Q1

## Goal
Promote the archive's existing toolchain/sysroot/sanitizer substrate into a first-class **Toolchain Productization Contract**: a reviewable boundary for **what exact Rust toolchain family was provisioned, what stdlib/sysroot profile was built or imported, how that variant was activated or reused, what runtime-analysis or hardening lane actually ran, and what later firmware / release / safety / support / assistant consumers may legitimately conclude**.

This contract should sit:
- **above** local rustup state, CI shell fragments, per-repo linker folklore, target-dir cache luck, and one-off sanitizer jobs;
- **below** broader release, safety, compatibility, and support narratives;
- and **beside** Workspace Environment, Build Interop, Cargo Artifact, Compatibility Claims, Safety-Critical Assurance, and Observability rather than replacing any of them.

The point is not to invent a new toolchain manager.
The point is to stop losing truth whenever a Rust team says “we built this with a custom toolchain” and no one can later tell whether that meant a rustup override, a rebuilt stdlib, a compiler-pinned custom target, an instrumented runtime, or all four.

## Why this seam matters now
The case for a first-class toolchain-productization contract is much stronger in 2026 than it was even a year ago:
- the 2026 flagship themes keep **Building blocks** centered on rebuilding std with custom flags and integrating Cargo into larger build systems;
- the accepted `build-std` goal is explicitly about an MVP that could be stabilized, not a forever-experimental escape hatch;
- Cargo's current unstable `-Z build-std` flow still requires `rust-src`, nightly Cargo, nightly rustc, and passing the flag to all Cargo invocations;
- rustup still models toolchains, components, targets, profiles, and directory-sensitive overrides as distinct control surfaces;
- rustup's cross-compilation docs still say target stdlib installation is not enough because linkers and SDKs are often also required;
- rustc custom-target docs still warn that target JSON properties are unstable and that compiler versions should be pinned;
- sanitizer support still strongly benefits from a recompiled and instrumented standard library, while the sanitizer-stabilization goal says production support needs a way to ship precompiled and instrumented standard libraries through rustup;
- Rust for Linux still needs stable foundations for custom std/core builds plus ABI-affecting, hardening, and sanitizer-related compiler options;
- and the end-of-2025 / early-2026 program-management updates say adopters like CPython are surfacing a very similar cluster of needs.

That combination means the missing contribution is no longer “one more cross-build helper” or “one more `build-std` wrapper”.
It is a **portable toolchain-as-product contract**.

## References (signals)
- Rust in 2026 / flagship themes:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- build-std goal:
  https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
- Cargo unstable `build-std` docs:
  https://doc.rust-lang.org/cargo/reference/unstable.html
- rustup cross compilation and overrides:
  https://rust-lang.github.io/rustup/cross-compilation.html
  https://rust-lang.github.io/rustup/overrides.html
- rustc custom targets:
  https://doc.rust-lang.org/rustc/targets/custom.html
- sanitizer docs:
  https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
- sanitizer stabilization goal:
  https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- Rust for Linux tooling goal:
  https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- program management update — end of 2025:
  https://blog.rust-lang.org/inside-rust/2025/12/19/program-management-update--end-of-2025/
- 2025 State of Rust survey results:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Working thesis
A worthy contribution here should make it easy to answer all of these without opening rustup state, CI YAML, Cargo config, and sanitizer notes side by side:
1. What exact **provisioned toolchain family** was available?
2. What exact **stdlib/sysroot profile family** was built or imported?
3. How was that variant **activated, selected, rejected, or reused** for this workspace or build?
4. What exact **runtime-analysis / hardening lane** ran, and what did or did not include instrumented std?
5. What later consumers — firmware, release, support, safety, incident review, assistants — may honestly import from the result?

If the design cannot answer those questions, then Rust still lacks the boring handoff that serious toolchain variants need.

## Contract shape
Read the existing toolchain substrate as a contract with six visibly separate layers:

### 1) Provisioning truth
The contract must preserve what toolchain ingredients actually existed:
- rustup channel / toolchain / profile / component / target identity;
- linked or path-based toolchain origin where relevant;
- external linker / SDK / C toolchain / sysroot provenance;
- local vs cached vs downloaded vs generated origin.

### 2) Stdlib / sysroot truth
The contract must preserve what standard-library family actually existed:
- rebuilt crates (`core`, `alloc`, `std`, `proc_macro`, `test`) where relevant;
- source provenance and compiler identity;
- target triple or compiler-pinned custom-target identity;
- baseline, hardened, instrumented, core-only, or ABI-modifying profile family;
- declared reuse and compatibility bounds.

### 3) Activation / reuse truth
The contract must preserve how the toolchain variant was actually selected:
- `rust-toolchain.toml`, rustup override, or direct `+toolchain` posture;
- Cargo target/linker/config activation posture;
- workspace-vs-CI-vs-external-build-system mode;
- mismatch / fallback / rejection reasons;
- reuse-vs-fresh-build distinction.

### 4) Runtime-analysis / hardening truth
The contract must preserve what execution posture actually ran:
- whether std itself was instrumented;
- which sanitizer, mitigation, or ABI-affecting lane was active;
- runtime libraries and mixed-language caveats;
- lane-specific comparability and unsupported residue.

### 5) Support / compatibility truth
The contract must preserve what a project can honestly claim afterward:
- supported target / host / compiler / profile family envelope;
- nightly-only vs stable vs pinned-compiler posture;
- what is experimental, partial, or organization-local;
- what compatibility consumers may summarize without pretending equivalence.

### 6) Consumer-handoff truth
The contract must tell later consumers what they may honestly import:
- firmware and release lanes can import provisioning + stdlib + activation truth;
- safety and incident lanes can import runtime-analysis / hardening truth;
- support and adoption lanes can import bounded support-envelope claims;
- assistants may summarize the pack, but must not claim more authority than the pack carries.

## What the MVP should look like in theory
A realistic v0 is not “solve cross compilation for all of Rust”.
It is:
- one schema family for provisioning, stdlib/sysroot identity, activation/reuse, runtime-analysis, and bundle packaging;
- one stock-rustup proof;
- one rebuilt-stdlib proof;
- one custom-target proof;
- one instrumented-runtime proof;
- and one downstream consumer import proof.

Required artifacts:
- `toolchain-provision-report/v0`
- `sysroot-profile-report/v0`
- `toolchain-activation-report/v0`
- `toolchain-runtime-lane-report/v0`
- `toolchain-support-summary/v0`
- `toolchain-product-pack/v0`

Required rules:
- keep **provisioning** distinct from **stdlib/sysroot identity**;
- keep **stdlib/sysroot identity** distinct from **activation/reuse**;
- keep **activation/reuse** distinct from **runtime-analysis / hardening**;
- keep **runtime-analysis / hardening** distinct from **support/compatibility summary**;
- keep **toolchain-product truth** distinct from **workspace-environment truth** and **release/distribution truth**.

## What the MVP should look like in practice
### Pilot 1 — stock + override lane
Show a pack that captures rustup toolchain/profile/target posture and directory-sensitive activation without claiming any rebuilt stdlib.

### Pilot 2 — rebuilt-stdlib lane
Show one `build-std`-driven sysroot/profile family with explicit compiler/source/profile identity and reuse bounds.

### Pilot 3 — compiler-pinned custom-target lane
Show one custom-target pack that makes compiler pinning and target-json instability explicit instead of hiding them in repo scripts.

### Pilot 4 — instrumented-runtime lane
Show a MemorySanitizer or ThreadSanitizer-capable lane with explicit instrumented-stdlib posture and runtime caveats.

### Pilot 5 — consumer import lane
Show one bounded import into firmware, release, safety, or support work without re-describing the whole toolchain story.

## Why this should be promoted instead of “just more build-std work”
The archive already had strong notes on Cross Toolchain, Sysroot Pack, Sanitizer Battery, firmware imports, and safety imports.
Those are still right, but the next sharpening move here is **not** another lower-level wrapper.

Why this promotion wins now:
- official signals are strongest on **stabilizable build-std**, **instrumented stdlib support**, **compiler-pinned custom targets**, and **serious adopter needs**, not on one new wrapper crate;
- the archive already has enough substrate to justify a composition layer;
- promoting the contract reduces the risk that one rustup override, one sysroot cache, one custom target JSON, or one sanitizer CI job silently defines the whole story.

So this revision promotes the **toolchain-variant / sysroot / activation / runtime-analysis boundary**, not the whole environment platform.

## Ranking impact
This does **not** reorder the archive's top band.
It adds one more explicit frontier beneath the current map:
- Build-State Evidence stays #1 overall.
- Adoption Navigation remains the strongest anti-tacit-knowledge frontier.
- Debuggability stays high.
- Rust inner-loop and Workspace Environment remain the clearest build/debug and environment bundle-shaping moves.
- Toolchain Productization Contract becomes the clearest next **toolchain-variant / sysroot / runtime-analysis-shaping** move.

That means it should sit below the broad build/debug/resource band, but above another round of ad hoc sysroot caching, cross-build shell glue, or sanitizer folklore.

## What not to build
Do **not** build:
- a rustup replacement;
- a universal cross-compilation manager;
- another `build-std` convenience wrapper pretending to solve provenance;
- a single “custom toolchain works” badge or score;
- or a release/support layer that swallows runtime-analysis and profile-family truth.

The winning contribution is thinner and more durable:
**publish explicit provisioning truth, explicit stdlib/sysroot-profile truth, explicit activation/reuse truth, explicit runtime-analysis truth, explicit support-envelope truth, and hand that off honestly to multiple consumers without flattening unlike toolchain families into one story.**
