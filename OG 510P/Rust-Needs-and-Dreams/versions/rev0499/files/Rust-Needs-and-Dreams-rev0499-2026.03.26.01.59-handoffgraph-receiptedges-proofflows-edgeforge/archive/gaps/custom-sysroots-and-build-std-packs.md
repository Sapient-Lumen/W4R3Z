# Gap: custom sysroots and build-std packs

## The need
Rust is much closer than before to making `build-std` a real, stable foundation rather than a niche nightly experiment. But even if Cargo lands a blessed way to rebuild `core` / `alloc` / `std`, teams will still need a shared way to **cache, reuse, distribute, activate, and verify** those rebuilt sysroots.

Right now, the workflow is fragmented:
- Cargo’s current `-Z build-std` flow is still early, nightly-only, and requires `rust-src` plus passing the flag on every invocation.
- The build-std project goal explicitly targets an MVP that can be stabilized, including explicit std dependencies and a standard way to use rebuilt standard-library artifacts.
- Rust-for-Linux and related low-level users need custom std/core builds on stable foundations.
- Sanitizer and exploit-mitigation docs already recommend rebuilding the standard library when enabling options like CFI or Control Flow Guard.
- Custom targets remain compiler-pinned and depend on build-std today.

Primary sources:
- build-std project goal (2025H2):
  https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
- Program update announcing build-std RFCs:
  https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/
- Cargo unstable docs for `-Z build-std`:
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Rust for Linux tooling/compiler goals:
  https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
  https://rust-lang.github.io/rust-project-goals/2025h2/Rust-for-Linux-compiler.html
- Sanitizer / mitigation docs showing rebuilt std requirements:
  https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
  https://doc.rust-lang.org/beta/unstable-book/compiler-flags/control_flow_guard.html
- Custom targets depend on build-std today:
  https://doc.rust-lang.org/rustc/targets/custom.html

## Why existing kits do not cover it
- **Cross Toolchain Kit** provisions compilers, SDKs, and sysroots in the generic sense. It does not define the identity or portability of a *rebuilt Rust standard library*.
- **Repro Build Kit** verifies whether artifacts can be rebuilt; it should consume sysroot facts instead of inventing them.
- **Sanitizer Battery Kit** records analysis profiles/results; it should attach the instrumented-stdlib facts produced elsewhere.
- **Build Extension Kit** is about declarative build steps and artifact uplift, not the lifecycle of custom std artifacts.

## What “good” looks like
A small shared substrate:
- `sysroot-intent/v0` — what standard-library rebuild is desired and why.
- `sysroot-pack/v0` — portable manifest for the built sysroot artifacts.
- `sysroot-activation/v0` — how a workspace/toolchain consumes that sysroot.
- `sysroot-report/v0` — what was actually built, reused, warned on, or rejected.
- `cargo sysroot` — reference UX for build / pack / verify / activate.

## Why this matters
Without this layer, every org that needs hardened std builds, tier-3/custom targets, Rust-for-Linux-style `build-core`, size-tuned embedded sysroots, or specialized codegen ends up building bespoke cache keys, artifact naming, activation conventions, and trust stories.

That is exactly the kind of high-leverage ecosystem seam this archive should prioritize: not “another custom build pipeline”, but one **reviewable contract** that many workflows can share.
