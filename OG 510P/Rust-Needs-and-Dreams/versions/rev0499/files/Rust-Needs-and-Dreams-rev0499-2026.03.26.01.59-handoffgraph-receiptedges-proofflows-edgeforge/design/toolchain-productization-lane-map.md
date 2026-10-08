# Design: Toolchain Productization Lane Map (stock rustup toolchains, build-std rebuilds, reusable sysroot packs, custom targets, activation rules, and instrumented runtime families)

## Goal
Make the archive more precise about **what kind of toolchain/product claim is actually being made**.

Rust’s toolchain story is getting stronger, but the ecosystem still talks too often as if one phrase — “custom toolchain support” — names one coherent thing.
It does not.
A stock rustup toolchain with extra targets installed, a nightly `-Z build-std` rebuild, a cached prebuilt sysroot pack, a compiler-pinned custom-target workflow, a host-vs-target activation configuration, and an instrumented standard library for sanitizer work are **different but connected** lanes.

The worthy contribution here is therefore not another cross-build wrapper or one more `build-std` convenience helper.
It is a **portable lane map and evidence boundary** that lets tools say which toolchain lane they are using, which identities and policies actually attach to it, where reuse is lossy, and which downstream consumers may reuse the claim honestly.

Read this together with:
- [`design/toolchain-productization-stack.md`](./toolchain-productization-stack.md)
- [`design/toolchain-productization-pilot-program.md`](./toolchain-productization-pilot-program.md)
- [`design/cross-toolchain-kit.md`](./cross-toolchain-kit.md)
- [`design/sysroot-pack-kit.md`](./sysroot-pack-kit.md)
- [`design/sanitizer-battery-kit.md`](./sanitizer-battery-kit.md)
- [`proposals/epic-toolchain-productization-stack.md`](../proposals/epic-toolchain-productization-stack.md)

## Why this note is needed now
The current official and near-official signals line up around one conclusion: Rust needs a better **toolchain-product contract**, not just more build helpers.

- The `build-std` goal is explicitly about an MVP that could be stabilized, and its motivation section keeps low-level/custom cases explicit: non-precompiled targets, non-baseline target features, ABI-changing flags, exploit mitigations, different `cfg`s, and even a blessed way to build at least `core` without Cargo for Rust-for-Linux-like users.
  https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
- Cargo’s current unstable docs still keep the experimental lane sharp: `-Z build-std` requires `rust-src`, requires nightly Cargo and nightly rustc, and must be passed to all Cargo invocations.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- rustup’s cross-compilation docs keep the stock rustup lane honest: `rustup target add` only installs the Rust standard library for a target, while linkers and SDKs are often still required separately.
  https://rust-lang.github.io/rustup/cross-compilation.html
- rustup’s override docs prove activation is its own lane. Toolchain shorthand, `RUSTUP_TOOLCHAIN`, directory overrides, `rust-toolchain.toml`, default toolchains, and pinned `components` / `targets` / `profile` are all explicit selection surfaces.
  https://rust-lang.github.io/rustup/overrides.html
- Custom-target docs keep compiler-pinned target identity explicit. Target JSON properties are unstable, the schema is version-coupled, and the docs say to always pin the compiler when using custom targets.
  https://doc.rust-lang.org/rustc/targets/custom.html
- The 1.93 release notes tightened the sysroot relationship further by making rustc search `/lib/rustlib/<target-triple>/target.json` under the sysroot. That is a strong signal that target description and sysroot packaging/transport are becoming more connected in practice.
  https://doc.rust-lang.org/beta/releases.html
- Cargo’s unstable `target-applies-to-host` / `host-config` docs show that host-versus-target activation remains a real seam. Cargo explicitly calls the current dual behavior around `linker` and `rustflags` confusing, and offers new knobs because host artifacts and target artifacts often need different configuration truths.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The sanitizer-support goal and the 2026 flagship page keep an instrumented-runtime lane explicit: stabilization of MemorySanitizer and ThreadSanitizer needs a way to provide **precompiled and instrumented standard libraries**.
  https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The end-of-2025 program update says CPython exploration is surfacing needs similar to Rust for Linux — `build-std`, platform support, sanitizer support — which is exactly the kind of large-adopter pressure that turns local toolchain folklore into an ecosystem seam.
  https://blog.rust-lang.org/inside-rust/2025/12/19/program-management-update--end-of-2025/

## The lane map

### Lane 1 — Stock rustup-distributed lane
**What it is**
- Toolchains and target stdlibs installed and selected through ordinary rustup distribution surfaces.
- Stable/beta/nightly or versioned channels, optional extra targets/components, and no rebuilt stdlib.

**Why it matters**
- This is the baseline lane most Rust users and many CI systems actually inhabit.
- It is the cleanest place to record channel/toolchain identity, component/profile/target inventory, and normal rustup selection behavior.

**What the archive should preserve**
- toolchain channel/version identity,
- installed targets/components/profile,
- rustup override posture,
- whether the target stdlib is upstream-distributed rather than rebuilt,
- and which facts remain outside rustup (linker, SDK, external sysroot).

**What it should not pretend**
- that `rustup target add` solves the whole cross-build problem,
- that stock rustup identity implies custom-flag or custom-target compatibility,
- or that installed-target inventory says anything about runtime instrumentation.

### Lane 2 — Local build-std rebuild lane
**What it is**
- On-demand standard-library rebuilds driven by `-Z build-std` or equivalent future upstream workflows.
- Typically per-workspace/per-invocation and still close to local build state.

**Why it matters**
- This lane is where many of the real motivating use cases first become possible.
- It is also where current friction is most obvious: nightly requirements, `rust-src`, repeated flag passing, and partial-support boundaries.

**What the archive should preserve**
- requested std scope (`core`, `alloc`, `std`, `proc_macro`, `test`),
- source provenance,
- compiler/channel identity,
- feature/config/codegen knobs,
- and whether the rebuild remains local/ephemeral versus exported.

**What it should not pretend**
- that “we can rebuild std” already means “we can reuse or review this stdlib later”,
- that local target-dir state is a transport format,
- or that a build-std lane automatically solves external-build-system consumers.

### Lane 3 — Reusable sysroot-pack lane
**What it is**
- Rebuilt std/core artifacts packaged, hashed, transported, and reused deliberately.
- Cached/canonicalized sysroot profiles rather than one-shot local rebuilds.

**Why it matters**
- This is the missing portability step between experimental rebuild and real productization.
- It is the lane firmware, CI, release, and safety/security consumers actually need if they are going to compare or import toolchain variants honestly.

**What the archive should preserve**
- pack identity and hash,
- exact compiler/source/target/profile family,
- compatibility or reuse policy,
- produced std artifacts,
- and activation/import receipts.

**What it should not pretend**
- that a sysroot pack is just a cache directory,
- that reuse rules are obvious from the target triple alone,
- or that transport/reuse can be reconstructed later from shell history.

### Lane 4 — Custom-target lane
**What it is**
- Compiler-pinned target JSON workflows, including `core`-only or `alloc`-only builds and tier-3-like target experiments.
- Any lane where target identity is not simply a built-in triple with upstream-distributed assumptions.

**Why it matters**
- This is where toolchain/productization has to stop pretending target identity is already stable.
- Target JSON, schema version, compiler version, and sysroot contents become one coupled subject.

**What the archive should preserve**
- target JSON identity/hash,
- compiler version coupling,
- built-in versus custom target origin,
- supported std scope,
- and mismatch/failure reasons.

**What it should not pretend**
- that custom targets are as stable as built-in targets,
- that a target triple string captures the full target contract,
- or that custom-target reuse can ignore compiler drift.

### Lane 5 — Activation and host/target split lane
**What it is**
- The rules by which a workspace or external orchestrator chooses the compiler, sysroot, linker, runner, rustflags, and host-vs-target behavior.
- rustup overrides, `rust-toolchain.toml`, Cargo `[target]` config, `host-config`, `target-applies-to-host`, runners, and build-dir/target-dir posture.

**Why it matters**
- “Which toolchain exists?” and “Which toolchain was actually used for this artifact?” are not the same truth.
- Host artifacts, build scripts, plugins, tests, and target artifacts can require different configuration contracts even inside one build.

**What the archive should preserve**
- activation source (rustup override, toolchain file, Cargo config, explicit CLI, external orchestrator),
- host-versus-target config posture,
- linker/runner/rustflags selection,
- build-dir/target-dir storage posture when relevant,
- and reason-coded mismatch or fallback behavior.

**What it should not pretend**
- that provisioning equals activation,
- that host and target artifacts always share one flag/linker story,
- or that successful local builds prove the activation policy was deliberate.

### Lane 6 — Instrumented / hardened runtime-family lane
**What it is**
- Toolchain variants where the stdlib and/or runtime are deliberately changed for sanitizers, hardening, or ABI-affecting/compiler-wide flags.
- Includes precompiled instrumented stdlibs and hardened profile families.

**Why it matters**
- This is the lane most likely to be flattened into “same compiler + same target” even though the actual runtime contract is materially different.
- It is also where official Rust work is actively pushing the ecosystem.

**What the archive should preserve**
- profile family (`instrumented`, `hardened`, `abi-modifying`, etc.),
- whether std itself was rebuilt/instrumented,
- runtime library assumptions,
- target/host support limits,
- and comparability boundaries for findings or performance.

**What it should not pretend**
- that local-crate instrumentation and instrumented-stdlib lanes are equivalent,
- that mitigation/sanitizer results generalize across profile families,
- or that one passing CI lane proves support for the whole runtime family.

### Lane 7 — External-build-system / foreign-orchestrator handoff lane
**What it is**
- Cargo-adjacent or non-Cargo consumers that still need to import toolchain/sysroot truth.
- `rustc`-direct flows, firmware or kernel-like orchestration, foreign build systems, and other tool-driven handoffs.

**Why it matters**
- Serious adopters often do not live entirely inside Cargo’s default UX.
- Toolchain productization becomes much more strategic when it can cross that boundary without flattening provenance.

**What the archive should preserve**
- Cargo-managed versus rustc-direct versus foreign orchestrator mode,
- imported toolchain/sysroot identities,
- handoff artifacts and environment contracts,
- and explicit lossiness if some local state is not exported.

**What it should not pretend**
- that Cargo-only evidence is automatically consumable by external builders,
- that external orchestration is a corner case unworthy of first-class modeling,
- or that handoff success means semantic equivalence.

## Adapter rules
A lane map becomes useful only if it names **lossy boundaries**.
The archive should therefore treat these as first-class adapter classes:

1. **stock rustup ↔ local build-std**
   - gains or loses rebuilt-stdlib identity, experimental requirements, and local-build assumptions.
2. **local build-std ↔ reusable sysroot pack**
   - gains or loses transport, cacheability, compatibility policy, and explicit reuse evidence.
3. **built-in target ↔ custom target**
   - gains or loses compiler-pinned target JSON identity and schema-coupled instability.
4. **provisioning ↔ activation**
   - gains or loses the exact selection/fallback/mismatch policy that determined what was actually used.
5. **baseline sysroot ↔ instrumented/hardened runtime family**
   - gains or loses runtime-library, ABI, and comparability assumptions.
6. **Cargo-managed ↔ foreign orchestration handoff**
   - gains or loses direct access to local build state and may require explicit exported environment/activation artifacts.

## What should change elsewhere in the archive
- **Toolchain Productization Stack** should remain the synthesis layer, but it should now cite this lane map as the rule for what must stay separate.
- **Sysroot Pack Kit** should remain the stdlib-identity anchor, but it should now stop sounding as if all rebuilt-stdlib stories are one lane.
- **Cross Toolchain Kit** should keep owning provisioning/handoff truth rather than silently swallowing activation or sysroot-family claims.
- **Sanitizer Battery Kit** should import instrumented-runtime-family truth instead of re-owning provisioning or activation.
- **Firmware Productization**, **Release Truth**, **Support Envelope**, and **Safety-Critical Evidence** should import only the toolchain lanes they actually consume instead of narrating their own hidden toolchain stories.
