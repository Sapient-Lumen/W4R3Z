# Epic: Sysroot Pack Kit

## One-liner
Make custom Rust standard-library builds reusable and auditable by standardizing a `cargo sysroot` workflow with `sysroot-intent/v0`, `sysroot-pack/v0`, `sysroot-activation/v0`, and `sysroot-report/v0`.

## Why it matters
Rust is actively pushing `build-std` toward a stable MVP, but many important users need more than “Cargo can rebuild std once on this machine”:
- tier-3 and custom-target users,
- embedded users tuning size/features,
- sanitizer / CFI / CFG workflows that need instrumented std,
- teams that will want precompiled or cacheable instrumented std distributions instead of every workflow rebuilding locally,
- Rust-for-Linux and similar low-level consumers,
- orgs that want remote caches, attestations, or policy around reusable custom sysroots.

Without a shared contract, every serious user invents bespoke cache keys, naming conventions, compatibility checks, and provenance stories.

Primary sources:
- build-std project goal:
  https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
- build-std RFC posting update:
  https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/
- Cargo unstable docs:
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Rust-for-Linux goals:
  https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
  https://rust-lang.github.io/rust-project-goals/2025h2/Rust-for-Linux-compiler.html

## Deliverables
1. Schemas + fixtures for:
   - `sysroot-intent/v0`
   - `sysroot-pack/v0`
   - `sysroot-activation/v0`
   - `sysroot-report/v0`
2. Reference `cargo sysroot` plugin or prototype adapter
3. Integration notes for:
   - build-std / explicit std-dependency workflows
   - custom targets
   - sanitizer / hardening builds
   - remote caches and reproducibility tooling
4. Ranked pilot guidance from [`design/toolchain-productization-pilot-program.md`](../design/toolchain-productization-pilot-program.md) covering:
   - instrumented-stdlib
   - hardened / ABI-modifying
   - custom-target / tier-3
   - shared-cache / CI
   - external-build-system handoff
5. Example attachment points for:
   - `sanitize-pack/v0`
   - `repro-pack/v0`
   - release / evidence packs

## Suggested rollout
- **v0.1:** manifest/report schemas + example packs for one normal target and one custom target
- **v0.2:** activation + compatibility rules; CI reuse prototype
- **v0.3:** attachments/integration with sanitizer, repro-build, and release evidence flows

## Ranking
**Tier 0/1**.
This is still upstream-dependent, but the official signal is now strong enough that the archive should treat it as an active frontier rather than a buried future bet. The right move is still to design the shared ecosystem contract now, not to pretend Cargo/rustup stabilization is already finished.
