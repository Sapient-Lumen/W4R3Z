## Execution note (rev0448)
Read this stack now through `design/toolchain-productization-execution-blueprint-2026Q1.md`.
The stack still matters, but the archive's current answer to “what should this seam actually ship?” is now explicit: **reference layer + report/pack command + profile/acceptance corpus**, not another environment manager, cache product, or one-off `build-std` wrapper.

# Design: Toolchain Productization Stack (Cross Toolchain + Sysroot Pack + Sanitizer Battery + Support / Release imports)

## Goal
Turn Rust toolchain variants into a **portable productization stack** — now explicitly read as a **Toolchain Productization Contract** — instead of leaving each custom-target, hardened, instrumented, or cross-build workflow to express itself through rustup state, Cargo flags, target JSON files, linker setup, CI cache folklore, and local shell history.

The stack should **not** replace rustup, Cargo, `build-std`, cross/zigbuild/xwin, sanitizer engines, or firmware/service release tooling.
It should make them compose better and make supported toolchain behavior reviewable.

This stack should now be read through the lens of [`design/toolchain-productization-lane-map.md`](./toolchain-productization-lane-map.md): stock rustup, local build-std, reusable sysroot packs, compiler-pinned custom targets, activation/host-target split rules, instrumented/hardened runtime families, and external-build handoff are related but non-equivalent lanes.


## Contract lens (rev0412)
Read this stack as the contract family beneath [`design/toolchain-productization-contract-2026Q1.md`](./toolchain-productization-contract-2026Q1.md).
The working separation is now:
- **provisioning truth**,
- **stdlib / sysroot truth**,
- **activation / reuse truth**,
- **runtime-analysis / hardening truth**,
- **support / compatibility truth**,
- and **consumer handoff truth**.

Default rule: never let one rustup override, one `build-std` invocation, one custom target JSON, one sysroot cache hit, or one sanitizer job silently claim all six layers at once.

## Why this note is needed now
Rust’s current signals say the missing problem is no longer “can Rust install targets and compile code at all?”
They say the missing problem is **what exact toolchain variant a Rust project can honestly claim to provision, activate, reuse, harden, instrument, and support**:
- the 2025H1 `build-std` goal is explicitly about an MVP that could be stabilized rather than the current experimental form;
- Cargo’s current unstable docs still say `-Z build-std` is early-stage, requires `rust-src`, requires nightly Cargo and nightly rustc, and must be passed to all invocations;
- rustup’s own model keeps toolchains, components, targets, profiles, linked toolchains, and directory overrides as separate surfaces;
- rustup cross-compilation docs explicitly say target stdlib installation is not enough because other tools such as linkers and SDKs are often required;
- custom targets explicitly warn that target JSON properties are unstable and that compiler versions should be pinned;
- the sanitizer-support goal says stabilizing MSan/TSan requires a way to provide **precompiled and instrumented standard libraries**, and the 2026 flagships page keeps that infrastructure active;
- Rust for Linux explicitly needs custom std/core builds plus stable support for ABI-affecting, hardening, and sanitizer-related compiler options;
- and the end-of-2025 program update says CPython exploration is surfacing a very similar cluster of needs.

Together, those signals argue that the missing contribution is **not** another `build-std` wrapper, another cross-build helper, or one more bespoke CI cache.
It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Cross Toolchain Kit: provisioning truth
Cross Toolchain owns the **toolchain acquisition and host-side provisioning surface**:
- rustup channel/toolchain identity;
- installed components / targets / profiles;
- linked or local toolchain origin when relevant;
- linker / SDK / sysroot / C toolchain provenance;
- generated Cargo config and environment handoff.

This layer answers questions like:
- “Which compiler, linker, SDK, and target stdlib were installed or referenced?”
- “Which parts came from rustup, and which came from external toolchains?”
- “What exactly was the host-side provisioning posture for this target?”

Design rule: **provisioning truth must not remain trapped in local rustup state or CI setup snippets**.

### 2) Sysroot Pack Kit: stdlib / sysroot truth
Sysroot Pack owns the **rebuilt standard-library identity surface**:
- std/core/alloc/proc_macro/test scope;
- source provenance and compiler identity;
- target or custom-target identity;
- baseline vs hardened vs instrumented vs custom-target profile family;
- built-artifact transport and compatibility rules.

This layer answers questions like:
- “Which stdlib profile was actually built?”
- “Can this sysroot be reused safely for this compiler/target/profile?”
- “What exact built std artifacts are being imported into this build?”

Design rule: **stdlib identity must not hide inside target-dir folklore or per-repo build caches**.

### 3) Activation lane: selection and reuse truth
Activation owns the **consumer-side selection surface**:
- rustup overrides and `rust-toolchain.toml` posture;
- Cargo target/linker/config selection;
- sysroot activation / toolchain selection / mismatch policy;
- workspace-vs-CI-vs-external-build-system mode.

This layer answers questions like:
- “How was this toolchain/sysroot chosen?”
- “What compatibility or mismatch rules were applied?”
- “Was this a deliberate reuse, a fallback, or an accidental local-state success?”

Design rule: **“we built it once” and “we are using it now” must remain separate truths**.

### 4) Sanitizer Battery Kit: runtime-analysis and hardening truth
Sanitizer Battery owns the **dynamic-analysis / instrumented-runtime lane**:
- whether std itself was instrumented;
- which runtime libraries and target modifiers were active;
- what finding classes were in scope;
- what observations are comparable versus lane-specific;
- what remained unsupported, partial, or inconclusive.

This layer answers questions like:
- “Did this run use an instrumented stdlib or only local-crate instrumentation?”
- “What mitigation or sanitizer lane actually ran?”
- “What runtime-analysis evidence can downstream users legitimately import?”

Design rule: **runtime-analysis truth must not be inferred from build flags or a passing CI job alone**.

### 5) Support / release / firmware / safety consumers
The stack matters when real consumers can import it honestly:
- **Firmware Productization** can import target/linker/sysroot/stdlib activation truth without redefining it;
- **Release Truth** can attach the toolchain/sysroot provenance of shipped artifacts without swallowing runtime-analysis evidence;
- **Support Envelope** can describe what target/provisioning/runtime floors are actually supported;
- **Safety-Critical Evidence** can import which stdlib/profile families and sanitizer lanes were used without pretending that provisioning equals proof;
- **Incident / observability / replay / atlas** consumers can reuse selected facts without reverse-engineering the machine state that produced a binary.

Design rule: **consumers import selected toolchain-productization facts; they do not redefine the stack**.

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust environment manager.”
It is a portable boring stack with clear boundaries:

1. **provisioning truth first**
   - prove rustup/external-toolchain/linker/SDK facts can travel in a reusable report for one real target;
2. **stdlib identity truth second**
   - prove rebuilt std/core identity and profile families can be packaged and diffed honestly;
3. **activation truth third**
   - prove workspaces, CI, and external builds can name how they selected or rejected a toolchain/sysroot;
4. **runtime-analysis truth fourth**
   - prove sanitizer and hardening lanes can import std/runtime provenance without flattening everything into one security story;
5. **consumer imports fifth**
   - prove firmware, release, support, and safety consumers can reuse the same facts.

An eventual aggregate artifact may exist, but it should be a **thin linked pack of imported artifacts**, not a mega-schema that erases provisioning truth, stdlib truth, activation truth, and runtime-analysis truth.

## Proposed aggregate artifact family
A plausible aggregate lane is:
- `toolchain-product-envelope/v0`
  - subject identity, selected target/profile, and imported artifact pointers;
- `toolchain-product-observation-report/v0`
  - what was actually provisioned, built, activated, or imported;
- `toolchain-product-diff-report/v0`
  - provisioning / sysroot / activation / runtime-analysis drift between two toolchain variants;
- `toolchain-product-pack/v0`
  - thin bundle linking lane-classified toolchain facts:
    - `toolchain-pack/v0`
    - `sysroot-pack/v0`
    - `sysroot-activation/v0`
    - optional `sanitize-pack/v0`
    - optional support / release / firmware / safety imports

The point is not one new toolchain oracle.
The point is a **reviewable toolchain-as-product handoff**.

## Ranked first execution lanes
1. **instrumented stdlib lane**
   - best first exporter because the sanitizer-support goal explicitly needs precompiled and instrumented standard libraries.
2. **hardened / ABI-modifying lane**
   - proves “same target triple” is not enough identity for serious low-level consumers.
3. **custom-target / tier-3 lane**
   - proves compiler version + target JSON + stdlib profile must travel together.
4. **shared-cache / CI lane**
   - proves reuse can become explainable and policyable instead of hidden cache luck.
5. **external-build-system lane**
   - proves Cargo and non-Cargo orchestration can share the same imported toolchain truths.

## Non-goals
- replacing rustup or the eventual upstream `build-std` design;
- another universal cross-compilation manager;
- collapsing rustup provisioning, stdlib variants, and runtime-analysis into one fake “custom toolchain” score;
- pretending sanitizer or mitigation results are interchangeable across profile families;
- flattening Cargo-managed and external-build-system activation into one story.

## Archive implications
- The archive should now treat **Cross Toolchain Kit + Sysroot Pack Kit + Sanitizer Battery Kit** as an explicit **Toolchain Productization Stack** in frontier and priority discussions.
- Future revisions should prefer **toolchain provisioning truth, stdlib profile identity, activation / reuse evidence, and runtime-analysis provenance** over another `build-std` wrapper, cross-build convenience layer, org-local cache, or one-off CI script collection.
- When Firmware, Release, Support, Safety, or Incident stacks touch target/toolchain readiness, they should import toolchain-productization artifacts rather than re-describe build environments from scratch.

## Read this together with
- `gaps/toolchain-variants-sysroots-cross-builds-and-sanitizer-support-contracts.md`
- `design/toolchain-productization-lane-map.md`
- `design/toolchain-productization-pilot-program.md`
- `design/cross-toolchain-kit.md`
- `design/sysroot-pack-kit.md`
- `design/sanitizer-battery-kit.md`
- `design/sanitizer-battery-pilot-program.md`
- `design/firmware-productization-stack.md`
- `design/safety-critical-evidence-stack.md`

## References (signals)
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
- rustup overrides:
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
