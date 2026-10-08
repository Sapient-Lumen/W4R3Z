---
id: P-0460
title: Unsafe Field Invariant Ledger Kit — field-authority receipts, mutation-lane reports, trusted-constructor witnesses, and drift-aware invariant bundles above Rust’s emerging unsafe-field model
status: idea
domains: [unsafe, language, verification, docs, review, devtools, safety]
last_reviewed: 2026-03-22
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h1/unsafe-fields.html
  - https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
  - https://www.ralfj.de/blog/2016/01/09/the-scope-of-unsafe.html
---

# Problem

Rust now has a much sharper language-level story for **field-carried safety invariants** than it did a year ago.
The unsafe-fields goal says fields that carry library safety invariants should be explicitly marked, and operations that could violate those invariants should require `unsafe` context. The std-contracts goal is simultaneously pushing safety assumptions toward machine-readable preconditions, postconditions, and invariants. The 2026 flagships then go further and name **normative unsafe documentation** as part of the safety-critical building-block agenda.

That creates a very specific ecosystem gap:

- today, many field invariants still live only in comments, module privacy, constructor folklore, or reviewer memory;
- tomorrow, more of that structure may become part of the language and standard-library contract story;
- but maintainers, adopters, and auditors still need a **boring, reviewable artifact layer** now.

The missing crate is therefore **not** the unsafe-fields language feature.
It is **not** a proof assistant.
It is **not** just another “unsafe inventory” linter.

The missing crate is an **invariant ledger** that tells other people:

1. which fields carry soundness-relevant invariants,
2. who is allowed to initialize or mutate them,
3. which safe wrappers are trusted to preserve those invariants,
4. what witness evidence exists,
5. and how that story changed across releases.

# What it provides

## Core review artifacts

### 1. `field-authority.receipt.json`
Declares where a field invariant comes from and who currently owns it.
Fields should include:
- field path and enclosing type
- authority source (`doc_comment`, `manual_manifest`, `contract_import`, `unsafe_field_syntax`, `review_note`, `unknown`)
- invariant class (`length`, `initialization`, `discriminant`, `aliasing`, `layout`, `state_machine`, `other`)
- human-readable invariant summary
- owner / review lane
- confidence class and unresolved notes

### 2. `mutation-lane.report.json`
Explains which functions, methods, traits, macros, or generated paths can mutate the field and under what posture.
Fields should include:
- mutator identity and visibility
- mutation lane (`unsafe_direct`, `trusted_safe_wrapper`, `constructor_only`, `drop_only`, `generated_code`, `unknown`)
- required preconditions
- whether mutation is interior / alias-sensitive / cross-thread sensitive
- manual-review gaps

### 3. `trusted-constructor.receipt.json`
Records the constructors and reconstitution paths that are allowed to establish the invariant.
Fields should include:
- constructor / parser / deserializer identity
- initialization completeness class
- validation steps performed
- postconditions claimed
- imported witness ids
- partial-trust or manual-review status

### 4. `invariant-witness.report.json`
States what evidence touched the invariant and what it did **not** cover.
Fields should include:
- witness kind (`tests`, `miri`, `loom`, `contracts`, `fuzz`, `manual_review`, `other`)
- scope of observation
- verdict (`passed`, `failed`, `partial`, `not_run`)
- evidence strength (`strong_for_claimed_scope`, `advisory`, `weak`, `manual_review_required`)
- non-claims list

### 5. `field-contract-drift.diff.json`
Compares two revisions and classifies drift.
Categories should include:
- `field_added`
- `authority_source_changed`
- `mutation_scope_widened`
- `mutation_scope_narrowed`
- `trusted_constructor_added`
- `trusted_constructor_removed`
- `witness_strength_changed`
- `comment_only_change`
- `manual_review_required`

### 6. `unsafe-field-bundle.manifest.json`
Portable manifest joining the receipts, source excerpts, notes, and repro commands needed for review.

## CLI sketch

- `cargo unsafe-field init` — create starter ledger and review vocabulary
- `cargo unsafe-field inventory` — find candidate invariant-bearing fields and likely mutators
- `cargo unsafe-field check` — compare the ledger against current source reality
- `cargo unsafe-field diff old/ new/` — classify invariant drift between revisions
- `cargo unsafe-field bundle` — emit a portable audit bundle

# What the crate should provide other people

1. **A field-level contract inventory** instead of scattered comments and private-module folklore.
2. **A mutation-lane map** that shows where safe code can still threaten soundness.
3. **A constructor-trust story** that makes initialization assumptions visible.
4. **A witness report** that says what tests, Miri, contracts, or manual review actually touched.
5. **A release-review diff** so downstream teams can see whether field authority or mutation scope changed.
6. **A bridge** from today’s manual ledgers to tomorrow’s native unsafe-field / contract substrate.

# Persona / who it’s for

- maintainers of unsafe foundational crates
- library authors with internal invariants around length, initialization, discriminants, aliasing, or state-machine phase
- safety reviewers and auditors
- downstream teams deciding whether a crate’s unsafe core is legible enough to adopt
- tool authors experimenting with contract imports or unsafe-field-aware review tools

# Users & user stories

- **Maintainer**: “Show me every field in this crate whose invariant matters to soundness, and which methods are trusted to mutate it.”
- **Reviewer**: “This PR adds a safe helper. Did it widen mutation authority or only refactor an existing constructor?”
- **Auditor**: “Export one compact bundle that ties invariant claims to mutators, constructors, and witnesses.”
- **Adopter**: “I do not need a proof of soundness; I need to know whether field invariants are explicit enough to review.”
- **Tool author**: “Use one stable ledger format now, then attach native unsafe-field or contract data later.”

# Prior art (and why it’s insufficient)

- The unsafe-fields goal names the field-invariant problem clearly.
- The std-contracts goal explains how contracts can describe preconditions, postconditions, and invariants.
- Safety-critical Rust planning now treats normative unsafe documentation as important shared substrate.
- Miri, tests, fuzzers, and manual audits can all produce useful evidence.
- “The Scope of Unsafe” remains the conceptual warning that safe code can invalidate unsafe assumptions.

What is still missing is a **receiver-facing artifact layer** for field invariants.
Today’s tools can tell you that a program executed, a test failed, or an unsafe block exists. They still do not give other people one compact answer to:

- which fields are authority-bearing,
- how mutation is controlled,
- which constructors are trusted,
- and what evidence actually covers those claims.

# Design goals

1. **Field-first** — focus on invariant-bearing fields, not every unsafe expression.
2. **Authority-explicit** — every invariant should say where its authority came from.
3. **Mutation-honest** — widening safe mutation scope must be visible and diffable.
4. **Witness-bounded** — do not overclaim what tests, Miri, or contracts proved.
5. **Bridge-ready** — useful today, but able to import future language and std-contract substrate.
6. **Audit-friendly** — optimize for review, handoff, and release comparison.

# MVP surface

- minimal types:
  - `UnsafeFieldLedger`
  - `FieldAuthorityReceipt`
  - `MutationLaneReport`
  - `TrustedConstructorReceipt`
  - `InvariantWitnessReport`
  - `FieldContractDrift`
  - `UnsafeFieldBundle`
- minimal functions:
  - `inventory_candidate_fields()`
  - `load_ledger()`
  - `check_mutation_lanes()`
  - `collect_witness_reports()`
  - `diff_field_contracts()`
  - `write_bundle()`
- feature flags:
  - `cargo`
  - `serde`
  - `rustdoc`
  - `miri`
  - `contracts`
  - `loom`

# Compatibility story

- Must work with ordinary stable Rust today using explicit manifests and conservative source analysis.
- Can later import native unsafe-field syntax, contract attributes, or richer rustdoc/JSON exports when they exist.
- Should support advisory mode for teams still discovering invariants.
- Must preserve `unknown`, `partial`, and `manual_review_required` instead of inventing certainty.

# Conformance & fixtures

- `Vec`-style length and initialization invariants.
- tagged-union or state-machine discriminant invariants.
- alias-sensitive intrusive/container fields.
- one fixture where a safe helper silently widens mutation authority.
- one fixture where comments exist but authority source remains unresolved.
- one fixture where Miri passes but the witness does not cover the trusted safe mutator gap.

# Path to boring stability

- Stabilize the ledger and diff schemas before clever inference.
- Start with explicit manifests and conservative checks.
- Treat mutator discovery as advisory when macros/generated code blur exactness.
- Add deeper tool adapters only after the core vocabulary proves useful.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A library and cargo subcommand that inventories candidate invariant-bearing fields, records field authority and trusted mutators explicitly, emits a mutation-lane report plus witness report, and packages those into a compact review bundle.

# De-risk plan

1. Start with manual ledgers and conservative source analysis.
2. Focus first on a few invariant families: length, initialization, discriminants, and phase/state fields.
3. Make `mutation_scope_widened` the first-class drift verdict.
4. Validate on one small unsafe crate before broadening scope.
5. Keep imported witness evidence advisory until the authority vocabulary settles.

# Non-goals

- Not a proof that a crate is sound.
- Not a replacement for language support, Miri, or formal verification.
- Not a full unsafe-audit platform for every UB concern.
- Not a claim that every internal invariant must be public.
- Not a promise to perfectly analyze every macro or generated mutator.

# Architecture & API sketch

```rust
pub struct FieldAuthorityReceipt {
    pub field_path: String,
    pub invariant_summary: String,
    pub authority_source: AuthoritySource,
}

pub fn inventory_candidate_fields(root: &Path) -> Result<Vec<FieldCandidate>>;
pub fn check_mutation_lanes(ledger: &UnsafeFieldLedger, root: &Path) -> Result<Vec<MutationFinding>>;
pub fn collect_witness_reports(ledger: &UnsafeFieldLedger, root: &Path) -> Result<Vec<InvariantWitnessReport>>;
pub fn diff_field_contracts(old: &UnsafeFieldLedger, new: &UnsafeFieldLedger) -> FieldContractDrift;
pub fn write_bundle(bundle: &UnsafeFieldBundle, out: &Path) -> Result<()>;
```

Bundle draft:
- `unsafe-fields.toml`
- `field-authority.receipt.json`
- `mutation-lane.report.json`
- `trusted-constructor.receipt.json`
- `invariant-witness.report.json`
- `field-contract-drift.diff.json`
- `unsafe-field-bundle.manifest.json`
- `notes.md`

# Security / safety model

- Never imply that listed invariants are exhaustive unless the maintainer explicitly says so.
- Keep unknown mutation paths visible.
- Support path redaction and private-symbol redaction in exported bundles.
- Treat witness imports as evidence for review, not proof of correctness.
- Keep FFI, layout, and broader unsafe-obligation lanes explicit rather than silently swallowing them.

# Maintenance & governance plan

- Track unsafe-fields, std-contracts, and normative-unsafe-doc evolution closely.
- Keep the field vocabulary small and auditable.
- Maintain a public casebook of a few high-value invariant families.
- Publish guidance for when a ledger entry should move from `candidate` to `trusted`.

# Milestones

## 0.1
- ledger schema
- field-authority receipt
- mutation-lane report
- trusted-constructor receipt

## 0.2
- witness report import
- diffing
- rustdoc/Markdown rendering
- bundle export

## 1.0
- stable ledger schema
- optional contract and native-syntax adapters
- public fixture corpus
- review-oriented diff summaries

# Open questions

- Which invariant families are common enough to standardize first?
- How much source analysis is worth doing before the crate becomes brittle?
- What should count as a meaningful mutation-scope widening in reports?
- How should generated code and macro expansions participate in authority tracking?

# Sources

- Unsafe fields goal: https://rust-lang.github.io/rust-project-goals/2025h1/unsafe-fields.html
- Std contracts goal: https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- What does it take to ship Rust in safety-critical?: https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The Scope of Unsafe: https://www.ralfj.de/blog/2016/01/09/the-scope-of-unsafe.html
