---
id: P-0465
title: BorrowSanitizer Workflow & Evidence Kit — aliasing-profile manifests, FFI-boundary receipts, and minimized provenance-violation bundles for BorrowSanitizer-era Rust
status: idea
domains: [unsafe, ffi, compiler, sanitizers, memory, testing, security, devtools]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/borrowsanitizer.html
  - https://borrowsanitizer.com/
  - https://github.com/borrowSanitizer/bsan
  - https://rust-lang.github.io/rfcs/3559-rust-has-provenance.html
  - https://github.com/rust-lang/miri
---

# Problem

Rust’s 2026 goals now include **BorrowSanitizer**, an LLVM-based instrumentation tool meant to find violations of Rust’s aliasing model at runtime, especially across language boundaries where Miri cannot see enough and where native execution speed matters. The project goal is explicit that the aim is practical usefulness, broad language-feature support, and feature parity with Miri for aliasing violations.

That still leaves a missing workflow layer for ordinary teams:

- BorrowSanitizer is a moving toolchain and runtime, not yet a boring team artifact,
- aliasing bugs often involve FFI boundaries, generated bindings, or unsafe wrappers that are hard to summarize in a review,
- runtime findings need minimization, provenance context, and environment pinning to become actionable,
- and teams need a compact way to compare BorrowSanitizer findings with Miri expectations or local suppressions without pretending the semantics are settled.

The missing crate is not another sanitizer and not a new aliasing model.

The missing crate is a **workflow-and-evidence kit** that turns BorrowSanitizer-era findings into reviewable bundles for maintainers, unsafe-code auditors, and upstream tool authors.

# What it provides

- `bsan-profile.toml` — pins toolchain, target, runtime options, FFI interception policy, and reporting/redaction settings.
- `ffi-boundary-map.json` — inventory of Rust/C/C++ boundaries, generated bindings, unsafe wrappers, and suspected provenance-sensitive edges.
- `bsan-run.json` — normalized record of one run: toolchain revision, runtime config, input workload, and observed finding counts.
- `provenance-violations.json` — canonicalized findings like `retag_violation`, `dangling_provenance`, `alias_conflict`, `out_of_bounds`, `use_after_free`, and `manual_review_required`.
- `miri-compare.json` — optional side-by-side comparison against a Miri run or expectation corpus.
- `reduction.receipt.json` — minimized reproducer status, redactions, and known unresolved dependencies.
- `cargo bsan-evidence run` — capture one instrumented run into a receipt bundle.
- `cargo bsan-evidence reduce` — minimize one report conservatively.
- `cargo bsan-evidence compare` — compare runs across revisions or against Miri expectations.
- `*.bsanbundle.zip` — shareable artifact for bug filing, unsafe review, or CI triage.

# What the crate should provide other people

1. **A boring profile artifact** for BorrowSanitizer runs.
2. **An FFI-boundary receipt** that explains where aliasing-sensitive edges actually live.
3. **A minimized handoff bundle** for upstream issue reports.
4. **A comparison layer** between BorrowSanitizer findings, Miri expectations, and local suppressions.
5. **A bridge** between cutting-edge aliasing instrumentation and ordinary unsafe-code review.

# Persona / who it’s for

- maintainers of unsafe or FFI-heavy Rust code
- security and reliability engineers
- teams embedding Rust in C/C++ applications
- compiler/tooling contributors working on BorrowSanitizer itself

# Users & user stories

- **Unsafe-code maintainer**: “Show me the exact aliasing-sensitive boundary and minimized workload that triggered this finding.”
- **Security engineer**: “Compare this BorrowSanitizer report against our last run and our Miri expectation corpus.”
- **Compiler contributor**: “Get a compact bundle with the workload, target, runtime options, and reduced reproducer.”
- **FFI team**: “Keep track of which binding edges are provenance-sensitive enough to deserve focused testing.”

# Prior art (and why it’s insufficient)

- The BorrowSanitizer goal and project site show a concrete LLVM-based tool is under active development.
- Miri remains the precise interpreter-based reference point for many aliasing checks.
- RFC 3559 and related provenance work make the conceptual substrate sharper than before.

What remains missing is a **maintainer-facing evidence layer**: the thing that says which runtime profile was used, which FFI boundary mattered, what the finding looked like, whether it was reduced, and how it compares to Miri or prior runs.


## 2026-03-16 fixture-first refresh

This proposal is now stronger for two reasons.

### 1. The archive now keeps the lane distinct from general sanitizer workflow
**P-0434 Sanitizer Profile & Evidence Kit** already owns the broad ASan/TSan/MSan workflow story.
This proposal is stronger when it stays focused on:

- BorrowSanitizer-specific aliasing/provenance findings,
- FFI-boundary-aware interpretation,
- optional Miri comparison,
- and minimization receipts.

### 2. The receiver-facing artifact split is now explicit
The new fixture pack freezes the first useful artifact set:

- `bsan-profile`
- `ffi-boundary-map`
- `bsan-run.receipt`
- `provenance-violation`
- `miri-compare`
- `reduction.receipt`

That is the right shape because another maintainer needs more than raw stderr or a screenshot of one backtrace.

### 3. The first scenarios cover both FFI-heavy and Rust-heavy lanes
The initial scenarios now cover:

- a mixed Rust/C++ callback boundary where provenance and callback ownership interact,
- and a Rust-heavy pin/projection reborrow regression where comparison against a Miri lane is plausible but still not exact.

That variety keeps the proposal honest about both the opportunity and the uncertainty.


# Design goals

1. **Evidence-first** — findings should be exportable and reviewable.
2. **Boundary-aware** — FFI edges and generated bindings matter.
3. **Reduction-friendly** — minimization must be part of the story early.
4. **Model-honest** — record tool and semantics assumptions explicitly.
5. **Useful during churn** — valuable even while BorrowSanitizer itself evolves rapidly.

# MVP surface

- Minimal types: `BsanProfile`, `FfiBoundaryMap`, `BsanRunReceipt`, `ProvenanceViolation`, `MiriCompare`, `ReductionReceipt`, `BsanBundle`
- Minimal functions:
  - `inventory_boundaries()`
  - `capture_bsan_run()`
  - `normalize_findings()`
  - `compare_with_miri()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `miri`
  - `ffi`
  - `reducer`

# Compatibility story

- Must be useful before BorrowSanitizer is fully upstream or stable by treating toolchain identity as explicit input.
- Should remain useful after upstreaming because teams will still need profile bundles and reduction receipts.
- Must tolerate partial runtime support and evolving finding categories.
- Should never imply that the absence of findings proves absence of aliasing bugs.

# Conformance & fixtures

- One Rust-only aliasing-sensitive fixture.
- One mixed Rust/C boundary fixture.
- One generated-binding fixture.
- Goldens for `alias_conflict`, `out_of_bounds`, `use_after_free`, and `manual_review_required`.
- A paired Miri comparison fixture with “same finding,” “only in Miri,” and “only in BorrowSanitizer.”

# Path to boring stability

- Stabilize the profile and finding vocabulary before ambitious dashboards or policy engines.
- Start with run capture + reduction + comparison.
- Keep the provenance taxonomy intentionally compact.
- Add richer suppression/waiver stories only after teams trust the receipts.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that run one BorrowSanitizer-configured workload, inventory the relevant FFI boundary, capture normalized findings, optionally compare them against Miri, and export a minimized review bundle.

# De-risk plan

1. Start with explicit profile input and bundle export only.
2. Keep finding categories high-level and conservative.
3. Validate on one mixed-language repro before broadening scope.
4. Treat Miri comparison as optional and informational, not canonical proof.

# Non-goals

- Not a replacement for BorrowSanitizer or Miri.
- Not a new aliasing model.
- Not a generic memory-sanitizer framework.
- Not a security certification product.

# Architecture & API sketch

```rust
pub enum ProvenanceViolationKind {
    AliasConflict,
    RetagViolation,
    OutOfBounds,
    UseAfterFree,
    Unknown,
}

pub fn inventory_boundaries(root: &Path) -> Result<FfiBoundaryMap>;
pub fn capture_bsan_run(profile: &BsanProfile) -> Result<BsanRunReceipt>;
pub fn compare_with_miri(bsan: &BsanRunReceipt, miri: &MiriReceipt) -> MiriCompare;
pub fn write_bundle(bundle: &BsanBundle, out: &Path) -> Result<()>;
```

Bundle draft: `bsan-profile.toml`, `ffi-boundary-map.json`, `bsan-run.json`, `provenance-violations.json`, `miri-compare.json`, `reduction.receipt.json`, `notes.md`.

# Security / safety model

- Never treat a clean run as proof of correctness.
- Record exact toolchain revision and runtime configuration.
- Support redaction of proprietary paths, symbols, and test inputs.
- Label model or feature-support gaps explicitly in the receipt.

# Maintenance & governance plan

- Track BorrowSanitizer’s upstream integration and runtime evolution closely.
- Keep finding categories and profile schema versioned.
- Maintain fixtures spanning Rust-only and mixed-language cases.
- Publish guidance for interpreting mismatches between BorrowSanitizer and Miri.

# Milestones

## 0.1
- profile schema
- run capture
- bundle export

## 0.2
- reduction receipts
- Miri comparison
- FFI boundary inventory

## 1.0
- stable receipt schema
- CI adapters
- curated repro corpus

# Open questions

- What is the smallest useful violation taxonomy for exported receipts?
- How much boundary inventory can be automated versus requiring local annotation?
- Which comparison classes between Miri and BorrowSanitizer matter most to ordinary maintainers?

# Sources

- BorrowSanitizer goal: https://rust-lang.github.io/rust-project-goals/2026/borrowsanitizer.html
- BorrowSanitizer site: https://borrowsanitizer.com/
- BorrowSanitizer GitHub: https://github.com/borrowSanitizer/bsan
- RFC 3559 Rust has provenance: https://rust-lang.github.io/rfcs/3559-rust-has-provenance.html
- Miri: https://github.com/rust-lang/miri
