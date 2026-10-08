---
id: P-0453
title: Safety Contract Consumer Kit — contract authority, consumer-coverage matrices, and semantic-lane receipts above Rust’s emerging contract attributes
status: idea
domains: [verification, unsafe, stdlib, tooling, contracts, testing, ci, formal-methods]
last_reviewed: 2026-03-23
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
  - https://github.com/model-checking/verify-rust-std
  - https://model-checking.github.io/kani/reference/experimental/contracts.html
  - https://github.com/creusot-rs/creusot
  - https://flux-rs.github.io/
---

# Problem

Rust is moving toward machine-readable safety contracts in the standard library. The project goal is explicit: contract attributes should support runtime checking when requested, and they should provide a compiler-facing interface that external tools can consume.

That is a huge opening — but it also reveals a likely ecosystem gap:

- contracts may exist, yet ordinary crate authors and verification users will still need a portable way to **extract, pin, diff, and consume** them,
- different downstream tools will want different views of the same contract surface,
- maintainers will need receipts showing which contracts were checked at runtime, assumed abstractly, or ignored,
- and today’s verification tools are powerful but do not share a boring default artifact for **contract consumption history**.

The missing crate is not another verifier.

The missing crate is a **consumer layer** that turns emerging Rust contracts into reusable artifacts for runtime checking, CI, and multiple external tools.


## 2026-03-23 refinement — make contract authority, consumer coverage, and semantic lane first-class

The archive now treats this proposal as stronger than “extract contracts and maybe hand them to tools”.
The sharper missing crate is a **contract-consumption honesty layer** that preserves three truths separately:

1. **contract authority** — where each clause came from and how it was extracted,
2. **consumer coverage** — which tools or modes actually consumed which clauses,
3. **semantic lane** — whether the result came from runtime checks, bounded model checking, deductive verification, refinement typing, separation logic, or manual review.

That means a stronger `0.1` should now emit at least:

- `contract-authority.receipt.json`
- `consumer-coverage.matrix.json`
- `semantic-lane.report.json`
- plus the earlier `contracts.snapshot.json`, `contracts.diff.json`, `contracts.receipt.json`, `contracts.runtime.json`, and bundle export.

The practical rule is simple: **do not let “contracts exist” or “tool X passed” silently become “all consumer lanes consumed the same contract surface with the same meaning.”**

# What it provides

- `contracts-profile.toml` — pins toolchain, extraction mode, runtime-check policy, and downstream adapters.
- `contracts.snapshot.json` — normalized extracted contract surface for a crate or dependency set.
- `contracts.diff.json` — records added, removed, or changed requires/ensures/invariant clauses.
- `contracts.receipt.json` — records which contracts were extracted, runtime-checked, handed to downstream tools, or skipped.
- `contract-authority.receipt.json` — records where each clause came from, how it was extracted, and what normalization/manual-review caveats remain.
- `consumer-coverage.matrix.json` — records which consumers or modes fully, partially, abstractly, or not at all consumed each clause.
- `semantic-lane.report.json` — records whether a result belongs to runtime checks, bounded model checking, deductive verification, refinement typing, separation logic, or another lane.
- `contracts.runtime.json` — runtime-check results for opted-in tests or harnesses.
- `cargo contracts-consume extract` — pull the current contract surface into a stable-on-top snapshot.
- `cargo contracts-consume diff` — compare contract snapshots across versions or toolchains.
- `cargo contracts-consume check` — run opted-in runtime checking profiles and emit receipts.
- `*.contractsbundle.zip` — shareable bundle for CI, review, or verification-tool handoff.

# What the crate should provide other people

1. **A boring authority story** for machine-readable safety contracts.
2. **A coverage matrix** for “which contracts did we actually use, and which ones did we not?”
3. **A semantic-lane report** that keeps runtime checks, model checking, deductive proofs, refinement typing, and manual review distinct.
4. **A bridge** between compiler-emitted contract substrate and downstream tools without pretending their semantics are identical.
5. **A diffable ledger** for reviewing contract-surface and consumption changes just like API changes.

# Persona / who it’s for

- maintainers of unsafe or verification-heavy crates
- teams depending on unsafe std APIs and wanting stronger guardrails
- verification-tool authors building on common contract substrate
- CI/release engineers for high-assurance systems

# Users & user stories

- **Unsafe crate maintainer**: “Extract and diff the standard-library contracts our code relies on when upgrading toolchains.”
- **Verification engineer**: “Export one contract snapshot that Kani-, Creusot-, or Flux-adjacent tooling can ingest.”
- **CI owner**: “Run a runtime-check profile in tests and keep a receipt of what was actually enforced.”
- **Auditor**: “Review whether a dependency change weakened or strengthened a safety contract we rely on.”

# Prior art (and why it’s insufficient)

- The Rust project goal and `verify-rust-std` establish real contract substrate and a real verification agenda.
- Kani, Creusot, and Flux prove there is meaningful downstream demand for machine-readable specifications.

What remains missing is a **shared consumer artifact layer** above those tools: extraction, snapshotting, diffing, and runtime-check receipts.

# Design goals

1. **Contract-first** — treat contracts as reviewable surface, not buried compiler trivia.
2. **Cross-tool** — one snapshot should serve multiple downstream consumers.
3. **Runtime-optional** — runtime checks are opt-in profiles, not hidden cost.
4. **Diffable** — contract changes should be easy to review in PRs and upgrades.
5. **Conservative** — do not pretend one tool’s semantics are the universal truth.

# MVP surface

- Minimal types: `ContractSnapshot`, `ContractClause`, `ContractDiff`, `ContractReceipt`, `RuntimeCheckProfile`
- Minimal functions:
  - `extract_contracts()`
  - `diff_contracts()`
  - `run_runtime_profile()`
  - `export_bundle()`
  - `render_summary()`
- Feature flags:
  - `serde`
  - `cargo`
  - `runtime-checks`
  - `kani`
  - `creusot`
  - `flux`

# Compatibility story

- Should work even while contract attributes remain experimental by recording toolchain and format assumptions.
- Can begin with extraction and snapshotting before any deep adapter story is stable.
- Must keep compiler-version and contract-surface provenance explicit.
- Should treat downstream-tool exports as adapters, not as the core schema.

# Conformance & fixtures

- Snapshot fixtures for small unsafe std-facing examples.
- Goldens for added precondition, weakened postcondition, unchanged extraction, and runtime-check-only cases.
- Example adapters for one or two downstream consumers.
- Runtime profile fixtures proving opt-in overhead and coverage surfaces remain visible.

# Path to boring stability

- Stabilize the snapshot and receipt schema before pursuing many adapters.
- Start with extraction + diff + runtime-check receipts.
- Keep contract syntax/semantics provenance explicit in every artifact.
- Prefer adapters that preserve uncertainty over falsely “translating” every clause perfectly.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A library and cargo subcommand that extract a normalized contract snapshot, diff two snapshots, optionally run an opt-in runtime-check profile, and emit a cross-tool receipt bundle.

# De-risk plan

1. Start with extraction and diff only.
2. Add one lightweight runtime-check mode before any ambitious multi-tool translation layer.
3. Treat all downstream-tool exports as clearly caveated adapters.
4. Validate usefulness on one unsafe-heavy crate and one verification-oriented workflow.

# Non-goals

- Not a new verification engine.
- Not a replacement for Kani, Creusot, Flux, or future tools.
- Not a promise that every contract can be translated losslessly to every consumer.
- Not a silent always-on runtime assertion framework.

# Architecture & API sketch

```rust
pub struct ContractSnapshot {
    pub toolchain: String,
    pub clauses: Vec<ContractClause>,
}

pub fn extract_contracts(profile: &ContractsProfile, root: &Path) -> Result<ContractSnapshot>;
pub fn diff_contracts(old: &ContractSnapshot, new: &ContractSnapshot) -> ContractDiff;
pub fn run_runtime_profile(profile: &RuntimeCheckProfile) -> Result<ContractReceipt>;
pub fn export_bundle(bundle: &ContractsBundle, out: &Path) -> Result<()>;
```

Bundle draft: `contracts-profile.toml`, `contracts.snapshot.json`, `contracts.diff.json`, `contracts.receipt.json`, `contracts.runtime.json`, `notes.md`.

# Security / safety model

- Runtime checking is opt-in and explicitly profiled.
- Every artifact must record the toolchain and extraction assumptions used.
- Support redaction of private paths and dependency names in shared bundles.
- Never claim a downstream proof tool consumed more of the contract surface than it actually did.

# Maintenance & governance plan

- Track contract-attribute evolution and version snapshots carefully.
- Keep the core snapshot schema small and adapter-neutral.
- Maintain example adapters and caveat docs for downstream tools.
- Publish guidance for interpreting changed contracts during toolchain upgrades.

# Milestones

## 0.1
- contract snapshot schema
- extraction
- version-to-version diff

## 0.2
- runtime-check profiles
- one downstream adapter
- bundle export

## 1.0
- stable snapshot/receipt schema
- multiple adapters
- CI/review integrations

# Open questions

- What is the smallest useful normalized contract schema?
- How should runtime-check results and tool-consumption results be represented together?
- Which downstream adapter is worth supporting first to prove the concept?

# Sources

- Instrument the Rust standard library with safety contracts: https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- `verify-rust-std`: https://github.com/model-checking/verify-rust-std
- Kani contracts: https://model-checking.github.io/kani/reference/experimental/contracts.html
- Creusot: https://github.com/creusot-rs/creusot
- Flux: https://flux-rs.github.io/
