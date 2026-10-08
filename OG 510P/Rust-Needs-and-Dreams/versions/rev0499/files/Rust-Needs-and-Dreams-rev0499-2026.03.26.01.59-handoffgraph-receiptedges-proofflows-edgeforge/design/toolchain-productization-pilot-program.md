# Design: Toolchain Productization pilot program

## Why this deserves promotion now
The archive already had the right ingredients — **Sysroot Pack Kit**, **Cross Toolchain Kit**, and **Sanitizer Battery Kit** — but not a crisp execution answer to the shared problem they are converging on.

That shared problem is **toolchain productization**:
- not just “can Rust build this target here?”
- but “can teams name, cache, distribute, activate, review, and trust *which* Rust standard library and adjacent target toolchain they are actually using?”

This is becoming strategically important because official Rust work is no longer treating custom std / instrumented std / hardened std as rare edge cases:
- `build-std` is being pushed toward a stabilizable MVP;
- 2026 flagships explicitly include sanitizer support that needs **precompiled and instrumented standard libraries**;
- Rust-for-Linux needs a blessed way to rebuild std plus ABI-affecting/hardening flags;
- and late-2025 project updates say other large adopters (for example CPython exploration) are surfacing a very similar cluster of needs.

So the missing contribution is not another bespoke cache or another cross-build wrapper. It is a shared artifact and workflow layer for **productized Rust toolchain variants**.

## Key primary sources
- build-std goal: https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
- Rust in 2026 / flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- sanitizer support goal: https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- sanitizer docs: https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
- Rust-for-Linux tooling goal: https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- program management update — October 2025: https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/
- program management update — end of 2025: https://blog.rust-lang.org/inside-rust/2025/12/19/program-management-update--end-of-2025/

## Strategic framing
Treat this as a shared band:
- [`design/sysroot-pack-kit.md`](./sysroot-pack-kit.md) — owns rebuilt Rust std/core identity, compatibility, activation, and reuse.
- [`design/cross-toolchain-kit.md`](./cross-toolchain-kit.md) — owns provisioning / SDK / linker / C toolchain handoff.
- [`design/sanitizer-battery-kit.md`](./sanitizer-battery-kit.md) — owns dynamic-analysis lanes and consumes sysroot/runtime provenance when std itself is instrumented.

This pilot program exists so those three layers compose without collapsing into one mega-tool. It now works together with [`design/toolchain-productization-lane-map.md`](./toolchain-productization-lane-map.md), whose job is to keep stock rustup, build-std, reusable sysroot packs, custom targets, activation rules, instrumented runtime families, and external handoff distinct while the pilots are executed.

## Posture classification
- **Sysroot Pack Kit:** evidence substrate / companion kit.
- **Cross Toolchain Kit:** companion kit.
- **Sanitizer Battery Kit:** companion consumer with some upstream-adjacent pressure.

The archive should *not* pretend to upstream all of this at once. The credible move is to prove the artifact boundaries and pilot lanes outside Cargo/rustup first.

## The first ranked pilot lanes

### 1) Instrumented-stdlib lane
**Why first**
This is the clearest signal from current official work. The sanitizer-stabilization goal explicitly says MemorySanitizer and ThreadSanitizer need infrastructure to provide **precompiled and instrumented standard libraries**, and the unstable-book docs still recommend rebuilding and instrumenting std for sanitizer workflows.

**What to build**
- `sysroot-intent/v0` with `profile_family = instrumented`
- `sysroot-pack/v0` for the instrumented std artifacts
- `sysroot-activation/v0` expressing how the instrumented std is selected
- `toolchain-pack/v0` reference to the surrounding linker/SDK/toolchain facts when relevant
- `sanitize-runtime-profile` / `sanitize-pack` attachments that name whether std, only local crates, or mixed-language boundaries were instrumented

**Why it matters**
This pilot proves the archive is solving a real packaging and review problem, not merely renaming `-Z build-std`.

### 2) Hardened / ABI-modifying lane
**Why second**
Rust-for-Linux explicitly calls out ABI-affecting and mitigation-related compiler flags plus the need for a blessed way to rebuild std. This is where “which stdlib did we actually link?” becomes operationally important.

**What to build**
- explicit `profile_family = hardened`
- captured codegen / mitigation knobs in `sysroot-intent/v0`
- compatibility rules explaining when reuse is forbidden versus permitted
- reason-coded activation rejection for mismatched compiler / target / mitigation profiles

**Why it matters**
This lane forces the design to handle the uncomfortable truth that “same target triple” is not enough identity for serious low-level consumers.

### 3) Custom-target / tier-3 lane
**Why third**
The build-std goal and rustc target docs keep making clear that custom-target workflows are real, but target specs and compiler versions remain tightly coupled.

**What to build**
- `profile_family = custom-target`
- required target-spec identity / hash in every pack and activation file
- explicit failure reasons for target-spec mismatch and unsupported std scope
- cache/reuse examples for `core`-only and `alloc` lanes

**Why it matters**
This is where the archive proves that Sysroot Pack Kit helps niche-but-important users *without* pretending custom targets are as stable as tier-1 triples.

### 4) Shared-cache / CI lane
**Why fourth**
A contribution here becomes much more valuable if sysroot builds can move between CI jobs or workspaces deliberately instead of hiding in target-dir folklore.

**What to build**
- `sysroot-pack/v0` transport + hash stability rules
- cache-import / cache-reuse / rebuild-reason reports
- attachment points to build-cache and resource-evidence work
- policy examples for “reuse only exact compiler identity” versus “allow vetted compatible range”

**Why it matters**
This lane proves that productized toolchain variants are not only for safety-critical adopters; they also matter to ordinary CI economics.

### 5) External-build-system handoff lane
**Why fifth**
This is strategically important, but should not be first because it adds coordination cost and environmental complexity.

**What to build**
- `sysroot-activation/v0` for Cargo-managed, `rustc`-direct, and external-build-system modes
- explicit handoff guidance for mixed Cargo / non-Cargo orchestration
- provenance attachments that downstream systems can import instead of scraping local target directories

**Why it matters**
This is how the archive keeps the door open for Rust-for-Linux-style and large-organization workflows without making them the first blocker.

## Shared schema discipline
The archive should keep the following truths separate:
1. **Provisioning truth** — where the compiler / linker / SDK came from (`toolchain-pack/v0`).
2. **Stdlib identity truth** — what Rust std/core artifacts were built, from which sources, with which knobs (`sysroot-pack/v0`).
3. **Activation truth** — how a consumer selected and used that sysroot (`sysroot-activation/v0`).
4. **Runtime-analysis truth** — which sanitizer or dynamic-analysis lane actually ran, with what coverage and limitations (`sanitize-pack/v0`).

Those are related truths, not one truth.

## Design constraints
- Do **not** redefine `build-std` or rustup distribution itself.
- Do **not** invent a universal cross-compilation manager.
- Do **not** flatten exact identity, compatible-range reuse, and “best effort” local experiments into one trust story.
- Do **not** let sanitizer convenience erase whether std itself, local crates only, or mixed-language boundaries were instrumented.

## Success bar
This pilot program is successful when:
- teams can name and diff the stdlib/toolchain variant they are actually using;
- instrumented or hardened std builds stop living as hidden local state;
- cache reuse becomes explainable and policyable;
- adjacent kits stop inventing their own ad hoc sysroot identity fields;
- and upstream build-std / sanitizer / platform-support work has a plausible ecosystem-grade attachment point waiting for it.
