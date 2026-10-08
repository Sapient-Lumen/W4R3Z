---
id: P-0120
title: Unsafe Contract Auditor Kit — obligation maps, dynamic witnesses, and reviewable evidence bundles for unsafe Rust
status: idea
domains: [devtools, unsafe, verification, testing, safety, cargo]
last_reviewed: 2026-03-22
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
  - https://github.com/rust-lang/miri
  - https://doc.rust-lang.org/reference/behavior-considered-undefined.html
  - https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html
  - https://doc.rust-lang.org/reference/attributes.html
  - https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
---

# Problem

Unsafe Rust is getting more explicit, but the evidence story is still too folkloric for ordinary teams.

Today, teams that maintain unsafe code often mix together:

- handwritten `# Safety` docs,
- Miri runs,
- a few targeted tests,
- occasional Loom schedules,
- scattered assumptions about FFI or symbols,
- and human review notes in PRs.

Those pieces all matter, but they answer different questions.
A passing dynamic check is not the same thing as a contract source of truth, and neither is the same thing as an honest statement about what the checker could not observe.

Recent Rust work makes that gap sharper, not fuzzier:

- the 2026 safety-critical flagship explicitly calls for **normative unsafe documentation** and other safety-oriented tooling work;
- the 2025h1 std-contracts goal says the desired future is effectively **contract as code** and reports experimental contract attributes plus hundreds of annotated standard-library functions in a research fork;
- Rust 2024 makes some unsafe boundaries more explicit with `unsafe extern`;
- and the Reference keeps reminding us that `unsafe` never makes UB acceptable.

That means the missing crate is no longer “some way to run Miri.”
It is an **unsafe obligation and evidence kit** that makes unsafe review transportable, comparable, and honest about blind spots.

# What it provides

- `unsafe-contracts.toml` — local contract manifest for unsafe APIs, assumptions, obligations, and review owners.
- `contract-authority.receipt.json` — where each safety obligation came from: docs, contract attributes, imported manifests, standard-library imports, or manual-only declarations.
- `obligation-map.report.json` — inventory of unsafe sites/APIs, obligation classes, status, evidence linkage, and unresolved gaps.
- `interpreter-boundary.receipt.json` — what a dynamic witness could and could not observe, including FFI, network, process, platform, target, and model limits.
- `witness-fidelity.report.json` — what a passing or failing witness actually means, including confidence class and explicit non-claims.
- `unsafe-audit-bundle.manifest.json` — compact bundle manifest for receipts, logs, model/version information, and exported notes.
- `authority-import.receipt.json` — normalized receipt for imported authority from docs, contract attributes, std-contract substrate, upstream manifests, or manual local declarations.
- `obligation-drift.diff.json` — semantic drift report for obligation additions/removals/site moves/owner changes across revisions.
- `witness-comparison.report.json` — comparison object for witness results whose scope and meaning can be honestly compared.
- `cargo unsafe-audit` — runs selected dynamic witnesses, gathers receipts, and emits a review bundle instead of loose terminal output.
- `cargo unsafe-diff` — compares obligation maps and witness-fidelity reports across revisions or toolchain changes.

# What the crate should provide other people

1. **One obligation inventory** for unsafe code rather than safety comments hidden across modules and PRs.
2. **Contract-source truth** so a reviewer can tell whether an obligation came from normative docs, experimental attributes, imported upstream contracts, or manual annotation.
3. **Dynamic-evidence honesty** so a passing Miri or Loom run is never mistaken for total proof.
4. **Boundary visibility** for FFI, symbols, callbacks, targets, and other places where a local interpreter/model cannot see the whole story.
5. **Comparable bundles** that let another engineer diff unsafe posture across releases, refactors, or toolchain changes.
6. **A shared vocabulary** for crate authors, auditors, and downstream adopters evaluating unsafe abstractions.

# Persona / who it’s for

- maintainers of crates with meaningful unsafe surfaces
- teams adopting third-party unsafe crates in regulated or high-assurance contexts
- auditors and reviewers who need something stronger than “tests passed on nightly”
- project leads trying to keep unsafe debt legible across refactors

# Users & user stories

- **Maintainer**: “When someone edits unsafe code, I want the obligation map and witness receipts to change in reviewable ways.”
- **Reviewer**: “Show me which obligations are covered by dynamic witnesses and which are still manual review only.”
- **Downstream adopter**: “I want to understand a crate’s unsafe posture without reverse-engineering every `unsafe` block.”
- **Auditor**: “I need an exported bundle that states what the evidence does *not* prove.”

# Prior art (and why it’s insufficient)

- **Miri** catches important classes of UB, but it explicitly does not catch everything, has environment/FFI/platform limits, and is not by itself a crate-level evidence contract.
- **Loom** explores schedule interleavings, but it is about concurrency modeling, not aliasing/init/FFI proof.
- **Safety docs / `# Safety` sections** are valuable, but they are not yet a stable cross-project evidence format.
- **Experimental contract attributes / std-contracts work** are promising substrate, but not yet an end-user workflow or bundle format.

The missing layer is therefore a **contract-authority + obligation-map + witness-boundary + bundle** kit above those tools.

## 2026-03-22 refinement — imported authority, drift, and comparison should now be first-class

The strongest next refinement for **P-0120** is not another witness backend.
It is three more receiver-facing review objects:

- `authority-import.receipt.json` — what was imported from docs, contract attributes, std-contract substrate, or upstream manifests, and with what exactness;
- `obligation-drift.diff.json` — whether unsafe posture changed semantically or only moved sites;
- `witness-comparison.report.json` — whether two witness results can honestly be compared at all.

That is the layer other engineers need in order to review unsafe posture across refactors, releases, or toolchain changes.

# Design goals

1. **Obligation-first** — start from what must be true, not from which tool happened to run.
2. **Witness-honest** — keep evidence strength and blind spots explicit.
3. **Transportable** — make audit artifacts easy to hand to another person or system.
4. **Incremental** — begin with manifest + receipts + bundle, not full formal verification.
5. **Upstream-aligned** — reuse Rust’s evolving contract/documentation direction rather than inventing a parallel unsafe language.
6. **Diffable** — make posture drift across releases visible.
7. **FFI-aware** — never pretend local interpreters or model checkers can see opaque foreign behavior.

# MVP surface

- Minimal types: `UnsafeContractManifest`, `ContractAuthorityReceipt`, `ObligationMapReport`, `InterpreterBoundaryReceipt`, `WitnessFidelityReport`, `UnsafeAuditBundleManifest`
- Minimal functions:
  - `load_contract_manifest()`
  - `collect_unsafe_sites()`
  - `import_contract_authority()`
  - `run_miri_witness()`
  - `run_loom_witness()`
  - `capture_interpreter_boundary()`
  - `evaluate_witness_fidelity()`
  - `write_obligation_map()`
  - `bundle_unsafe_audit()`
- Feature flags:
  - `serde`
  - `cargo-metadata`
  - `miri`
  - `loom`
  - `git-diff`
  - `ffi`

# Compatibility story

- Works above today’s unsafe docs, unsafe attributes, Miri runs, and optional Loom scenarios.
- Records when obligations come from imported authority versus manual local declarations.
- Degrades honestly when the witness cannot model the boundary.
- Should be useful even before contract attributes stabilize, by treating authority source as a first-class field.
- Can integrate with CI, release reviews, and downstream assurance bundles.

# Conformance & fixtures

- tiny fixtures for aliasing-sensitive abstractions, initialization protocols, FFI callbacks, symbol obligations, and concurrency-only witnesses;
- goldens for `authority_from_docs`, `authority_missing`, `miri_partial_scope`, `ffi_out_of_scope`, `loom_schedule_only`, `authority_import_upgraded_but_gap_remains`, `obligation_sites_moved_without_semantic_closure`, `witness_scope_shifted`, and `manual_review_required` outcomes;
- corpus entries showing when `unsafe extern` or `unsafe(...)` attributes carry obligations orthogonal to memory-model witnesses.

# Path to boring stability

- Stabilize `unsafe-contracts.toml` and the four core receipt/report schemas first.
- Keep the first version focused on obligation inventory and witness honesty rather than automated proof claims.
- Grow importer support for future std-contracts / contract-attribute substrate only after the receipt model is trusted.
- Treat bundle comparability as a first-class feature so teams can gate unsafe drift conservatively.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A crate and cargo subcommand that ingest a lightweight unsafe contract manifest, inventory unsafe sites, run one or two selected dynamic witnesses, emit contract-authority / obligation-map / interpreter-boundary / witness-fidelity artifacts, and package them into one portable review bundle.

# De-risk plan

1. Start with Miri plus manual contract manifests.
2. Make Loom and FFI-aware receipts optional but explicit.
3. Treat imported or future contract-attribute authority as another source class, not a hard dependency.
4. Keep the artifact model honest about what remains manual-review only.

# Non-goals

- Not a proof that unsafe code is sound.
- Not a replacement for Miri, Loom, Kani, Creusot, or Verus.
- Not a generalized certification framework.
- Not a promise to infer every unsafe obligation automatically.

# Architecture & API sketch

```rust
pub struct ObligationMapReport {
    pub crate_id: String,
    pub unsafe_sites: Vec<UnsafeSite>,
    pub authority: ContractAuthorityReceipt,
    pub witnesses: Vec<WitnessFidelityReport>,
}

pub fn run_unsafe_audit(manifest: &UnsafeContractManifest, cx: &AuditContext) -> Result<UnsafeAuditBundleManifest>;
pub fn diff_obligation_maps(old: &ObligationMapReport, new: &ObligationMapReport) -> ObligationDiff;
```

Bundle draft: `unsafe-contracts.toml`, `contract-authority.receipt.json`, `obligation-map.report.json`, `interpreter-boundary.receipt.json`, `witness-fidelity.report.json`, `unsafe-audit-bundle.manifest.json`, `logs/`, `notes.md`, `repro/`.

# Security / safety model

- Preserve exact toolchain/model/witness provenance.
- Separate **obligation presence** from **evidence strength**.
- Preserve explicit boundary receipts when FFI, symbols, callbacks, or platform dependencies limit the witness.
- Never convert “witness passed” into “unsafe soundness proved.”

# Maintenance & governance plan

- Keep authority-source importers thin and versioned.
- Maintain a small witness taxonomy with stable non-claim language.
- Publish fixture packs for common unsafe-pattern families.
- Add stronger integrations only after the baseline bundle model is stable.

# Milestones

## 0.1
- manifest format
- unsafe-site inventory
- contract-authority receipt
- Miri witness + interpreter-boundary receipt
- bundle writer

## 0.2
- Loom witness support
- diffing between revisions
- FFI/manual-boundary annotations

## 1.0
- stable bundle schema
- richer source importers
- review-friendly HTML/doc rendering for obligation maps

# Open questions

- How much unsafe-site inventory can be extracted reliably versus declared manually?
- What is the smallest useful vocabulary for authority source classes?
- How should future contract attributes map into stable end-user receipts without overfitting to one experiment?

# Sources

- 2026 flagship goals / safety-critical work: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- 2025h1 std-contracts goal: https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- Miri: https://github.com/rust-lang/miri
- Rust Reference UB list: https://doc.rust-lang.org/reference/behavior-considered-undefined.html
- Rust 2024 `unsafe extern`: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html
- Rust Reference attributes / unsafe attributes: https://doc.rust-lang.org/reference/attributes.html
- safety-critical Rust write-up: https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

Treat `meta/unsafe-contract-auditor-product-plan-2026-03-22.md` as the working build sketch for **P-0120**.
The key new planning detail is that a worthy unsafe-audit crate should elevate **contract authority**, **obligation inventory**, **interpreter boundary**, and **witness fidelity** into first-class artifacts rather than flattening everything into one “Miri passed” story.
