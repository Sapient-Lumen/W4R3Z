# Unsafe Field Invariant Ledger product plan — 2026-03-22

This note turns **P-0460 Unsafe Field Invariant Ledger Kit** into a more concrete build plan.

## Product thesis

The worthy crate is not a verifier that promises soundness.
It is a **reviewable field-invariant workflow** that helps maintainers, auditors, and adopters answer five questions:

1. which fields carry soundness-relevant invariants,
2. where those claims came from,
3. who may initialize or mutate those fields,
4. what witnesses touched those claims,
5. and what changed across revisions.

## Core artifacts

### 1. `field-authority.receipt.json`
Records the authority source for each invariant-bearing field.
Key fields should include:
- crate / module / type / field identity
- authority source class (`doc_comment`, `manual_manifest`, `contract_import`, `unsafe_field_syntax`, `review_note`, `unknown`)
- invariant class
- summary text
- owner / review lane
- confidence class and unresolved notes

### 2. `mutation-lane.report.json`
Maps who can change the field and under what posture.
Key fields should include:
- mutator identity
- visibility
- lane (`unsafe_direct`, `trusted_safe_wrapper`, `constructor_only`, `drop_only`, `generated_code`, `unknown`)
- required preconditions
- aliasing / threading / reentrancy caveats
- manual-review gaps

### 3. `trusted-constructor.receipt.json`
Records the creation/reconstitution paths allowed to establish the invariant.
Key fields should include:
- constructor / parser / deserializer identity
- validation steps
- postconditions claimed
- completeness class (`fully_establishes`, `partially_establishes`, `manual_review_required`)
- linked witness ids

### 4. `invariant-witness.report.json`
States what evidence touched the field contract and what it did not cover.
Key fields should include:
- witness kind (`tests`, `miri`, `loom`, `contracts`, `fuzz`, `manual_review`, `other`)
- observation scope
- verdict (`passed`, `failed`, `partial`, `not_run`)
- evidence strength
- non-claims list

### 5. `field-contract-drift.diff.json`
Compares two revisions and classifies contract drift.
Key fields should include:
- old/new revision ids
- field identity
- drift categories
- severity / review recommendation
- linked evidence ids

### 6. `unsafe-field-bundle.manifest.json`
Portable manifest for receipts, source excerpts, repro commands, and notes.

## CLI sketch

- `cargo unsafe-field init` — generate starter manifest and review vocabulary
- `cargo unsafe-field inventory` — discover candidate invariant-bearing fields and likely mutators
- `cargo unsafe-field check` — validate current source against the declared ledger
- `cargo unsafe-field diff old/ new/` — compare field contracts between revisions
- `cargo unsafe-field bundle` — create portable review bundle

## Planned package structure

- library crate for artifact types and diff logic
- cargo subcommand for workspace execution
- optional rustdoc/Markdown rendering adapter

## Adoption sequence

### MVP
- manual ledger
- candidate field inventory
- field-authority receipt
- mutation-lane report
- trusted-constructor receipt
- bundle writer

### v0.2
- witness imports
- diff mode for release comparison
- CI helpers
- richer Markdown rendering

### v1
- importers for future unsafe-field syntax / std-contracts substrate
- broader fixture corpus
- interop with larger unsafe-audit and evidence-bundle lanes

## What this crate should explicitly refuse to do

- promise soundness,
- infer total coverage from one witness,
- collapse field invariants into all unsafe obligations,
- or pretend every team needs formal verification before the crate becomes useful.
