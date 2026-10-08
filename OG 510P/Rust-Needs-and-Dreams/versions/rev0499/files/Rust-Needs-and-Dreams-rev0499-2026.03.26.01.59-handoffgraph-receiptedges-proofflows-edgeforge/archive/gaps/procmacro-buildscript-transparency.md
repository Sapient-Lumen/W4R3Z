# Gap: Compile-time execution authority, determinism, and override truth

## Summary
`build.rs` scripts and procedural macros are not just “build tooling”; they are **compile-time execution surfaces** with real authority. Rust’s own docs make that explicit: procedural macros run during compilation with the same file-access and I/O posture as the compiler, and therefore carry the same security concerns as build scripts. Cargo’s build-script model is similarly powerful: scripts receive a wide environment, can emit linker and cfg instructions, can persist artifacts in `OUT_DIR`, and are expected not to mutate outside it. At the same time, Cargo already has one important escape hatch: when a crate uses `package.links`, the build script can sometimes be **overridden declaratively** so it does not run at all.

The ecosystem is moving in three directions at once:
- **sandbox / permissions** for build scripts,
- **WebAssembly or otherwise isolated execution lanes** for proc-macros,
- **language/tooling work that reduces the need for proc-macros or ad hoc build execution in the first place**.

What is still missing is a shared, reviewable boundary that keeps these truths separate instead of collapsing them into one fuzzy “safe build” story.

## What is missing
Rust still lacks one portable artifact family for compile-time execution that can answer all of the following cleanly:
1. **What units will run?** Build script, native proc-macro, wasm proc-macro, or links-override/no-run lane.
2. **What authority do they declare?** Filesystem, environment, network, process spawning, clock/time, toolchain metadata, native probing.
3. **What did they actually do?** Observed reads/writes/spawns/connects, redacted where necessary.
4. **What counts as an input?** Files, env vars, metadata, host/target assumptions, `rerun-if-*` declarations, system-library probing.
5. **How deterministic / cacheable are they?** Whether the execution lane is portable enough to feed user-wide caches, reproducible-build checks, or remote execution.
6. **What was waived or overridden?** Explicit org waivers, or declarative replacement of a `links` build script.
7. **How should policy consume it?** Reviewable verdicts and reason codes instead of scraped logs or ad hoc sandbox output.

Today those answers are scattered across Cargo docs, Rust Reference notes, project-goal experiments, custom sandboxes, and tribal knowledge.

## Ecosystem signals
- The Rust Reference says procedural macros run during compilation and therefore have the same file-access and security concerns as build scripts:  
  https://doc.rust-lang.org/reference/procedural-macros.html
- The Rust Reference also says `proc-macro` crates are always compiled for the host that built the compiler, even when the final crate targets something else; host/target lane truth is therefore first-class, not incidental:  
  https://doc.rust-lang.org/reference/linkage.html
- Cargo’s build-script docs say scripts receive many environment inputs, may write artifacts only into `OUT_DIR`, should not modify outside it, and should narrow re-run triggers with `rerun-if-*`; Cargo also supports overriding some `links` build scripts so they are not run at all:  
  https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Rust’s sandboxed-build-scripts goal explicitly targets opt-in sandboxing, per-crate permissions, explicit restriction of file/network/process access, one future interface for both build scripts and proc-macros, and even potential remote-execution / hermetic-build support:  
  https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- The compiler-team proposal for WebAssembly proc-macros argues that today’s native dynamic-library execution model creates reproducibility and security hazards, and that a wasm execution strategy could also improve build reuse across targets:  
  https://github.com/rust-lang/compiler-team/issues/876
- Rust’s declarative-macro-improvements goal explicitly tries to make more macros possible without proc-macros because proc-macros increase complexity, dependency footprint, and build time:  
  https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- The compiler-performance survey says stabilizing language features could remove the need for some build scripts or proc-macros and thereby improve build performance:  
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The user-wide build-cache goal says safe cache reuse depends on idempotence, and explicitly mentions future sandboxing work as the path to determining precise `build.rs` / proc-macro inputs:  
  https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html

## What “good” looks like
A worthy ecosystem contribution here would provide:
- a canonical inventory of compile-time execution units and lanes;
- declared capabilities that are narrow and explainable;
- observed-access evidence that can confirm or contradict declarations;
- explicit input-surface and determinism reports suitable for caching / repro / CI;
- clean distinction between “this executed under sandbox”, “this was replaced by metadata”, and “this lane is currently native / unsandboxed”;
- diffable reports and waivers that policy, trust, and release tools can consume.

The right contribution is **not** just another sandbox wrapper. It is a shared compile-time authority boundary for the whole ecosystem.
