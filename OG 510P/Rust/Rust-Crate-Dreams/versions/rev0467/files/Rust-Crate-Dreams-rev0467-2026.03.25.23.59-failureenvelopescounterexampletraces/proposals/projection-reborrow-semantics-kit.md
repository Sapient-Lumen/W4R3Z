---
id: P-0440
title: Projection & Reborrow Semantics Kit — projection-authority receipts, borrow-mode matrices, and Miri-backed semantics witnesses for smart-pointer APIs
status: idea
domains: [language, safety, testing, pinning, pointers, no-std, devtools, ffi]
last_reviewed: 2026-03-23
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/field-projections.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
  - https://crates.io/crates/pin-project
  - https://crates.io/crates/pin-init
  - https://crates.io/crates/reborrow-generic
  - https://crates.io/crates/moveit
  - https://github.com/rust-lang/miri
  - https://arxiv.org/abs/2504.14500
---

# Problem

Rust’s “Beyond the `&`” frontier is no longer hypothetical.
The 2026 flagship agenda explicitly calls out **field projections**, **reborrow traits**, and **in-place initialization**.
At the same time, the ecosystem already has real crates and real pressure in this area:

- `pin-project` for projection ergonomics,
- `pin-init` for pinned construction,
- `moveit` for in-place / C++-style construction pressure,
- `reborrow`, `relend`, and `reborrow-generic` for generalized reference ergonomics,
- Rust-for-Linux patterns that rely on pinned initialization and projection,
- and Miri as the practical undefined-behavior detector when unsafe abstractions get subtle.

What is still missing is **not** another projection macro, **not** another reference-like trait, and **not** a pretend formal proof engine.

What is missing is a **reviewable semantics-support layer** that lets a crate hand other people one honest answer to questions like:

- Which projection surface is authoritative?
- Which borrow/reborrow modes are actually supported?
- Which semantics were witnessed under ordinary tests versus Miri?
- Which aliasing / movement paths remain uncovered or manual-review-only?
- What changed across releases when the projection surface moved?

That gap matters because smart-pointer ergonomics are becoming a language-and-library frontier simultaneously.
The more real substrate exists, the more teams need a stable artifact layer above it.

# Product thesis

The worthy crate here is a **receiver-facing semantics kit**.
It should help maintainers, reviewers, adopters, and language-adjacent experimenters answer five questions:

1. which API or macro surface is authoritative for projection/reborrow claims,
2. which borrow-mode families are intentionally supported,
3. what witness evidence was actually collected,
4. which important paths remain caveated,
5. and what drifted across revisions.

# What it provides

- `projection-authority.receipt.json` — records which macro/manual/trait/API surface is authoritative for projection claims and which fields or wrappers are in scope.
- `borrow-semantics.matrix.json` — classifies which projection/reborrow modes are supported, caveated, unsupported, or manual-review-only.
- `semantics-witness.report.json` — records fixture families, ordinary-test outcomes, Miri outcomes, uncovered paths, and caveats.
- `projection-drift.diff.json` — compares two revisions and classifies surface, mode, witness, and caveat drift.
- `projection-support-bundle.manifest.json` — portable manifest joining authority, mode matrix, witness reports, fixtures, commands, notes, and source references.
- reusable fixture families for:
  - structural pin projection,
  - nested field projection,
  - generalized reborrowing,
  - `MaybeUninit` / out-pointer paths,
  - `UnsafeCell` / interior-mutation wrappers,
  - raw-pointer escape hatches,
  - and address-sensitive embedded fields.
- `cargo projection-semantics capture` — run declared fixtures and emit receipts.
- `cargo projection-semantics explain <case>` — explain authority, supported modes, and remaining caveats.
- `cargo projection-semantics diff old/ new/` — classify semantics drift between revisions.
- `cargo projection-semantics bundle` — emit a portable receiver-facing bundle.

# What the crate should provide other people

1. **Projection authority honesty** instead of “the macro exists, so support must be obvious.”
2. **Borrow-mode coverage** instead of one vague “supports projection/reborrow.”
3. **Witness-basis honesty** instead of flattening ordinary tests, Miri, and manual reasoning into the same claim.
4. **Reusable tricky fixtures** so advanced pointer crates can share pain instead of rediscovering it privately.
5. **Release-diff visibility** when an abstraction changes projection, pinning, or reborrow posture.
6. **Portable review bundles** that another team can inspect without reconstructing unsafe arguments from scratch.
7. **A migration bridge** between today’s crate patterns and tomorrow’s language support.

# Persona / who it’s for

- authors of smart-pointer, pinning, wrapper, and alias-sensitive crates
- Rust-for-Linux and embedded maintainers
- C++/Crubit / FFI-adjacent maintainers whose values are address-sensitive
- reviewers of unsafe abstractions
- language-adjacent experimenters comparing current crate patterns to future language features

# Users & user stories

- **Pointer-crate maintainer**: “Show that our projection API keeps its advertised borrow modes and pinning caveats intact.”
- **Reviewer**: “Give me one artifact telling me what was actually witnessed under Miri and what still needs human review.”
- **Rust-for-Linux-style maintainer**: “Validate pinned initialization plus projection patterns with a shared fixture corpus.”
- **Interop maintainer**: “Compare address-sensitive construction wrappers against projection/reborrow claims without pretending this is the full FFI contract.”
- **Language experimenter**: “Compare today’s macro/trait implementation with an experimental future language path.”

# Prior art (and why it’s insufficient)

- `pin-project` solves projection ergonomics for an important subset of pinned structs and enums, but it is not a shared receipt/witness layer.
- `pin-init` solves safe pinned initialization, but not the wider projection/reborrow evidence story.
- `moveit` solves in-place construction pressure, but not reviewable borrow/projection support truth.
- `reborrow`, `relend`, and `reborrow-generic` explore generalized reborrowing ergonomics, but they do not publish a common support contract above the abstraction.
- Miri is an essential UB detector, but a raw Miri run is not a portable semantics packet by itself.
- PinChecker shows that popular pinning APIs can still hide unsoundness; that strengthens the case for reusable witness discipline rather than weakening it.

What remains missing is the **contract/fixture/witness layer** above those tools.

# Design goals

1. **Authority first** — record which surface is being claimed before checking it.
2. **Mode-matrix honesty** — support must be expressed as specific borrow/projection modes.
3. **Witness-basis clarity** — distinguish ordinary tests, Miri, imported evidence, and manual review.
4. **Fixture-richness** — common sharp-edge cases matter more than generic prose.
5. **Language-evolution tolerance** — useful before and after future language support lands.
6. **Portable reviewability** — another engineer should be able to inspect the bundle later.
7. **Conservative claims** — a green witness run must not silently become “proved safe.”

# MVP surface

- Minimal types:
  - `ProjectionAuthorityReceipt`
  - `BorrowSemanticsMatrix`
  - `SemanticsWitnessReport`
  - `ProjectionSupportBundleManifest`
- Minimal functions:
  - `load_projection_profile()`
  - `capture_projection_authority()`
  - `derive_borrow_mode_matrix()`
  - `run_semantics_witnesses()`
  - `bundle_projection_support()`
- Feature flags:
  - `miri`
  - `pin`
  - `no-std`
  - `serde`
  - `html-report`

# Compatibility story

- Works with macro-based projection crates and hand-written unsafe abstractions.
- Useful for `std`, embedded, Rust-for-Linux-style, and interop-heavy crates where practical.
- Keeps future field-projection/reborrow language support as an **input to the same artifact model**, not as a replacement for artifacts.
- Must degrade honestly when Miri/platform coverage is incomplete.

# Conformance & fixtures

- structural pin projection fixtures,
- nested field and field-of-field projection fixtures,
- generalized reborrow trait fixtures,
- `UnsafeCell` / wrapper-view fixtures,
- `MaybeUninit` / out-pointer / partial-init fixtures,
- raw-pointer escape-hatch fixtures,
- goldens for `supported`, `caveated`, `unsupported`, `witnessed_under_miri`, `ordinary_tests_only`, and `manual_review_required` outcomes.

# Path to boring stability

- stabilize the receipt/report schemas before expanding fixture breadth;
- keep the borrow-mode taxonomy intentionally small;
- treat uncovered or manual-review-only paths as first-class output;
- refuse to imply proof from partial witnesses.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 24/30**

# Minimum lovable MVP

A crate that lets a smart-pointer or wrapper crate declare its authoritative projection surface, emit a small borrow-mode matrix, run reusable semantics fixtures under tests and Miri, and export one portable support bundle showing what was really witnessed and what remains caveated.

# De-risk plan

1. Start with structural pin projection and one generalized reborrow family.
2. Keep the initial borrow-mode vocabulary small and auditable.
3. Use real ecosystem crates as pilot adopters.
4. Treat witness gaps as product output, not failure to prettify.

# Non-goals

- Not a formal proof system.
- Not a replacement for `pin-project`, `pin-init`, `moveit`, or reborrow crates.
- Not a complete unsafe-contract auditor.
- Not a language design proposal in disguise.
- Not a promise that passing Miri equals semantic proof.

# Architecture & API sketch

```rust
pub struct ProjectionAuthorityReceipt {
    pub subject: String,
    pub authority_kind: AuthorityKind,
    pub scope: Vec<String>,
    pub caveats: Vec<String>,
}

pub struct BorrowSemanticsMatrix {
    pub subject: String,
    pub modes: Vec<BorrowModeVerdict>,
}

pub struct SemanticsWitnessReport {
    pub subject: String,
    pub ordinary_test_verdict: WitnessVerdict,
    pub miri_verdict: WitnessVerdict,
    pub uncovered_paths: Vec<String>,
    pub caveats: Vec<String>,
}

pub fn capture_projection_authority(profile: &ProjectionProfile) -> Result<ProjectionAuthorityReceipt>;
pub fn derive_borrow_mode_matrix(profile: &ProjectionProfile) -> Result<BorrowSemanticsMatrix>;
pub fn run_semantics_witnesses(profile: &ProjectionProfile, cx: &RunContext) -> Result<SemanticsWitnessReport>;
pub fn bundle_projection_support(out: &std::path::Path, bundle: &ProjectionSupportBundleManifest) -> Result<()>;
```

# Security / safety model

- Never treat a green witness run as proof of soundness.
- Preserve exact toolchain / Miri context where used.
- Keep uncovered modes and manual-review-only paths visible.
- Support redaction of local source paths in exported bundles.

# Maintenance & governance plan

- Maintain a shared corpus of sharp-edge projection/reborrow cases.
- Version the authority and borrow-mode vocabularies conservatively.
- Keep platform- or feature-specific fixtures clearly labeled.
- Encourage adapters rather than one monolithic crate-specific implementation.

# Milestones

## 0.1
- projection-authority receipt
- small borrow-mode matrix
- semantics witness report
- portable bundle manifest

## 0.2
- drift diff
- richer generalized-reborrow fixtures
- HTML explanation reports

## 1.0
- stable schemas
- broader ecosystem corpus
- CI adapters

# Open questions

- What is the smallest useful borrow-mode vocabulary for the MVP?
- Which witness gaps deserve dedicated output fields versus free-form caveats?
- How much of the authority surface can be captured automatically versus declared manually?
- Which ecosystem crates make the best pilot adopters?

# Sources

- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Field projections goal: https://rust-lang.github.io/rust-project-goals/2025h2/field-projections.html
- Reborrow traits goal: https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
- In-place initialization goal: https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
- `pin-project`: https://crates.io/crates/pin-project
- `pin-init`: https://crates.io/crates/pin-init
- `reborrow-generic`: https://crates.io/crates/reborrow-generic
- `moveit`: https://crates.io/crates/moveit
- `miri`: https://github.com/rust-lang/miri
- PinChecker: https://arxiv.org/abs/2504.14500
