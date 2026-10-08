---
id: P-0454
title: ABI Coherence Profile Kit — target-modifier profiles, exemption ledgers, and sysroot-coherence receipts for ABI-affecting compiler-flag workflows
status: idea
domains: [compiler, cargo, build, ffi, safety, ci, tooling, rust-for-linux]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rfcs/3716-target-modifiers.html
  - https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
  - https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
  - https://github.com/rust-lang/rust/issues/131837
  - https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
---

# Problem

Rust is finally treating ABI-affecting compiler flags as something that must be made explicit and checkable rather than tribal knowledge. RFC 3716 says rustc should record target modifiers in crate metadata and reject mismatches by default, while the Rust-for-Linux tooling goals make clear that real projects need whole-program flag coordination for code generation, hardening, and production sanitizer use.

That is good compiler hygiene — but it also exposes a practical ecosystem gap:

- teams need a boring way to declare **which flags are meant to be coherent across the entire build**,
- they need to track when the sysroot or rebuilt `core` / `alloc` / `std` was compiled under the same assumptions,
- they need reviewable records of every `unsafe-allow-abi-mismatch` exemption,
- and they need something more structured than shell snippets and CI environment variables when handing these builds to auditors, platform engineers, or upstream maintainers.

The missing crate is not another compiler-flag collection.

The missing crate is a **coherence profile layer** that turns ABI-affecting builds into reviewable artifacts.

# What it provides

- `abi-profile.toml` — pins toolchains, targets, ABI-affecting flags, allowed exemptions, and required sysroot policy.
- `abi.coherence.json` — normalized record of which crates, units, and sysroot artifacts were built under which flag set.
- `abi.exemptions.json` — every allowed mismatch, who requested it, why it exists, and what scope it applies to.
- `abi.sysroot.json` — whether `core` / `alloc` / `std` were rebuilt, with which flags, and which assumptions remain unverified.
- `abi.diff.json` — categories such as `fully_coherent`, `workspace_mismatch`, `sysroot_mismatch`, `dynamic_linking_unknown`, and `new_exemption_added`.
- `cargo abi-coherence plan` — produce the intended coherence profile for a workspace or target family.
- `cargo abi-coherence check` — verify actual build artifacts against the profile.
- `cargo abi-coherence diff` — compare two profiles or receipts across releases/toolchains.
- `*.abibundle.zip` — shareable artifact for CI, audits, bug reports, or platform handoff.

# What the crate should provide other people

1. **A boring whole-program flag contract** for hardening, sanitizers, target features, and Rust-for-Linux-style builds.
2. **An exemption ledger** for cases where mismatches are knowingly tolerated.
3. **A sysroot coherence receipt** that makes “we rebuilt std/core with the same assumptions” reviewable.
4. **A handoff artifact** for auditors, distro/toolchain teams, and compiler contributors.
5. **A bridge** between raw compiler flags and real build/release processes.

# Persona / who it’s for

- maintainers of low-level or safety-critical Rust code
- Rust-for-Linux and embedded build engineers
- teams using sanitizer or hardening profiles across whole programs
- distro/toolchain integrators
- compiler contributors triaging ABI-mismatch reports

# Users & user stories

- **Kernel maintainer**: “Show me which ABI-affecting flags we require on arm64 and whether rebuilt `core` matched them.”
- **Embedded team**: “Compare our code-size / hardening profile between two releases and see whether any exemption was added.”
- **Compiler contributor**: “Get a compact bundle showing where a workspace tripped a target-modifier mismatch.”
- **Release engineer**: “Block shipment unless the profile, sysroot receipt, and actual build all agree.”

# Prior art (and why it’s insufficient)

- RFC 3716 and the tracking work are giving rustc a correctness story for target modifiers.
- The Rust-for-Linux and build-std goals show that whole-program flag coherence and rebuilding the sysroot are real use cases, not edge-case theory.
- Sanitizer and hardening flags already exist in various unstable or target-specific forms.

What remains missing is a **maintainer-facing profile / exemption / receipt layer** above raw rustc and Cargo knobs.

# Design goals

1. **Coherence-first** — treat consistent flag application as the primary invariant.
2. **Sysroot-aware** — whole-program assumptions are not reviewable if the sysroot story is hidden.
3. **Exemption-explicit** — every mismatch waiver must be recorded.
4. **Conservative** — clearly mark dynamic-linking and prebuilt-artifact blind spots.
5. **Toolchain-neutral on top** — work with current unstable workflows while staying useful after stabilization.

# MVP surface

- Minimal types: `AbiProfile`, `FlagSet`, `AbiCoherenceReceipt`, `AbiExemption`, `SysrootReceipt`, `AbiDiff`
- Minimal functions:
  - `load_profile()`
  - `collect_receipt()`
  - `check_coherence()`
  - `diff_profiles()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `build-std`
  - `sanitizers`
  - `rust-for-linux`

# Compatibility story

- Must remain useful while many workflows are still unstable or partially stabilized.
- Can begin by wrapping explicit manifests plus observed metadata instead of waiting for perfect compiler support.
- Should model unknowns honestly when dynamic linking or externally produced artifacts are involved.
- Must stay distinct from general build-analysis tooling by centering **flag coherence**, not every rebuild cause.

# Conformance & fixtures

- Fixtures for arm64 target-modifier builds, x86 hardening profiles, sanitizer-enabled whole-program builds, and a rebuilt-`core` workflow.
- Goldens for `fully_coherent`, `workspace_mismatch`, `sysroot_mismatch`, and `new_exemption_added`.
- Example bundles with one acceptable exemption and one rejected mismatch.
- A small casebook for “same workspace, different target-feature profile” review.

# Path to boring stability

- Stabilize the profile and receipt schema before fancy policy engines.
- Start with explicit manifests and observed receipts, not inference-heavy magic.
- Make exemptions impossible to hide.
- Add richer sysroot introspection only after the core workflow is trusted.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that check one workspace against a declared ABI-affecting flag profile, emit a coherence receipt plus any exemptions, and bundle the exact toolchain/sysroot assumptions for review.

# De-risk plan

1. Start with manifest + receipt generation, not automatic build mutation.
2. Focus first on one or two flag families that are clearly ABI-affecting.
3. Treat sysroot unknowns as first-class output instead of pretending they are solved.
4. Validate on one Rust-for-Linux-style or embedded workspace before widening scope.

# Non-goals

- Not a replacement for rustc’s own mismatch checks.
- Not a new build system.
- Not a guarantee that every ABI hazard can be inferred from artifacts alone.
- Not a generic security certification framework.

# Architecture & API sketch

```rust
pub struct AbiExemption {
    pub flag_name: String,
    pub scope: String,
    pub reason: String,
}

pub fn load_profile(path: &Path) -> Result<AbiProfile>;
pub fn collect_receipt(profile: &AbiProfile, root: &Path) -> Result<AbiCoherenceReceipt>;
pub fn check_coherence(receipt: &AbiCoherenceReceipt) -> Vec<AbiFinding>;
pub fn write_bundle(bundle: &AbiBundle, out: &Path) -> Result<()>;
```

Bundle draft: `abi-profile.toml`, `abi.coherence.json`, `abi.exemptions.json`, `abi.sysroot.json`, `abi.diff.json`, `notes.md`.

# Security / safety model

- Every exemption must be explicit and attributable.
- Record the exact toolchain, targets, and flag sources used.
- Support path redaction and proprietary-target redaction in exported bundles.
- Never imply sysroot coherence when it was not directly observed.

# Maintenance & governance plan

- Track RFC 3716 implementation and ABI-affecting flag evolution closely.
- Keep the profile schema small and review-oriented.
- Maintain fixtures for real-world flag families and rebuild-std scenarios.
- Publish interpretation guidance for dynamic-linking blind spots and exemptions.

# Milestones

## 0.1
- profile schema
- receipt collection
- mismatch / exemption reporting

## 0.2
- sysroot receipts
- profile diffing
- bundle export

## 1.0
- stable receipt schema
- CI policy adapters
- public fixture corpus

# Open questions

- What is the smallest useful definition of “coherent enough” for real-world builds?
- How should dynamic linking and prebuilt system libraries be represented without overclaiming?
- Which ABI-affecting flags should be modeled first to prove the workflow?

# Sources

- RFC 3716 target modifiers: https://rust-lang.github.io/rfcs/3716-target-modifiers.html
- Rust-for-Linux tooling goal: https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- build-std goal: https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
- Tracking issue for ABI-altering `-C` flags: https://github.com/rust-lang/rust/issues/131837
- Sanitizer docs: https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
