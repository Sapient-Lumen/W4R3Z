# Projection & Reborrow Semantics product plan — 2026-03-23

This note turns **P-0440 Projection & Reborrow Semantics Kit** into a more concrete build plan.

## Product thesis

The worthy crate is not another projection macro and not another generalized-reference crate.
It is a **reviewable semantics workflow** that helps maintainers, auditors, and adopters answer five questions:

1. which projection surface is authoritative,
2. which borrow/reborrow modes are intentionally supported,
3. what witness evidence was collected,
4. which paths remain uncovered or manual-review-only,
5. and what changed across revisions.

## Core artifacts

### 1. `projection-authority.receipt.json`
Records which surface is authoritative for the support claim.
Key fields should include:
- subject / API id
- authority kind (`macro_generated`, `manual_impl`, `trait_family`, `wrapper_api`, `future_language_experiment`, `unknown`)
- authority source refs
- structurally-pinned scope
- wrapper / field scope
- declared caveats
- unresolved authority edges

### 2. `borrow-semantics.matrix.json`
Classifies supported borrow and projection modes.
Key fields should include:
- subject / profile id
- mode rows
- mode class (`shared_projection`, `mutable_projection`, `pinned_projection`, `nested_projection`, `generalized_reborrow`, `raw_escape_hatch`, `out_ptr_init_bridge`, `unknown`)
- verdict (`supported`, `caveated`, `unsupported`, `manual_review_required`)
- prerequisites / cfg / feature notes
- evidence refs

### 3. `semantics-witness.report.json`
States what was actually exercised.
Key fields should include:
- subject / fixture set
- ordinary-test verdict
- Miri verdict
- toolchain / execution basis
- fixture families exercised
- uncovered paths
- known false-confidence risks
- manual-review notes

### 4. `projection-drift.diff.json`
Compares two revisions and classifies semantics drift.
Key fields should include:
- old/new revision ids
- changed authority surface
- changed borrow-mode verdicts
- changed witness basis
- changed caveats / uncovered paths
- severity / review recommendation

### 5. `projection-support-bundle.manifest.json`
Portable manifest for profiles, receipts, fixture inputs, commands, source references, and notes.

## CLI sketch

- `cargo projection-semantics init` — generate starter profile and vocabulary
- `cargo projection-semantics capture` — execute declared casebook and emit receipts
- `cargo projection-semantics explain <case>` — explain authority, mode coverage, and witness caveats in receiver-facing language
- `cargo projection-semantics diff old/ new/` — compare projection/reborrow posture between revisions
- `cargo projection-semantics bundle` — create portable review bundle

## Planned package structure

- library crate for artifact types, fixture execution, and diff logic
- cargo subcommand for workspace execution and bundling
- optional adapters for `pin-project`, `pin-init`, `moveit`, and generalized-reborrow crates

## Adoption sequence

### MVP
- manual profile file
- projection-authority receipt
- small borrow-semantics matrix
- semantics-witness report
- bundle writer

### v0.2
- drift diff
- richer nested-projection and generalized-reborrow fixtures
- CI helpers

### v1
- adapter pack for major ecosystem crates
- broader no_std / Rust-for-Linux scenarios
- interop with in-place-init, unsafe-field, and unsafe-contract lanes

## What this crate should explicitly refuse to do

- define the official language semantics,
- collapse all pointer abstractions into one verdict,
- infer soundness from one green Miri run,
- or replace broader unsafe auditing.
