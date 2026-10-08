# In-Place Initialization Adoption product plan — 2026-03-22

This note turns **P-0447 In-Place Initialization Adoption Kit** into a more concrete build plan.

## Product thesis

The worthy crate is not a new initialization engine.
It is a **reviewable adoption workflow** that helps maintainers, auditors, and adopters answer five questions:

1. where the value was first initialized,
2. which constructor family / move semantics were actually used,
3. when the final address became authoritative,
4. how partial-init and cleanup work,
5. and what changed across revisions.

## Core artifacts

### 1. `placement-topology.receipt.json`
Records where initialization really happened.
Key fields should include:
- case id / type id
- topology class (`by_value_stack`, `heap_final_place`, `caller_provided_place`, `field_embed_place`, `ffi_out_ptr`, `unknown`)
- first-write site
- final-allocation site
- stack-bounce flag
- caller-provided storage flag
- caveats / unresolved inference

### 2. `constructor-lane.report.json`
Classifies constructor family and semantics.
Key fields should include:
- constructor family (`rust_by_value`, `pin_init`, `moveit_new`, `crubit_ctor`, `ffi_out_ptr`, `future_language`, `local_unsafe_adapter`)
- pin-required flag
- move semantics class (`rust_memcpy_move`, `cxx_constructor_move`, `no_move_after_commit`, `unknown`)
- direct-init vs pinned-only posture
- feature/cfg constraints
- comparison notes

### 3. `address-commit.receipt.json`
States when movement becomes forbidden.
Key fields should include:
- commit event id
- pin-begins-at
- move-forbidden-after
- inner-vs-outer commit points for embedded fields
- evidence source (`declared`, `inferred_from_api`, `fixture_witness`, `manual_review`)
- unresolved edges

### 4. `failure-cleanup.report.json`
Keeps fallible-init posture honest.
Key fields should include:
- fallible edges
- partial-init regions
- cleanup owner
- cleanup mechanism (`drop`, `rollback_code`, `not_initialized`, `manual_review`)
- leftover-initialized-state risk
- review notes

### 5. `init-transition.diff.json`
Compares two revisions and classifies strategy drift.
Key fields should include:
- old/new revision ids
- changed constructor family
- changed address-commit boundary
- changed cleanup posture
- changed topology class
- severity / review recommendation

### 6. `init-support-bundle.manifest.json`
Portable manifest for profiles, receipts, fixture inputs, source references, raw commands, and notes.

## CLI sketch

- `cargo init-adopt init` — generate starter profile and vocabulary
- `cargo init-adopt capture` — execute declared casebook and emit receipts
- `cargo init-adopt explain <case>` — explain topology, constructor lane, and cleanup posture in receiver-facing language
- `cargo init-adopt diff old/ new/` — compare initialization posture between revisions
- `cargo init-adopt bundle` — create portable review bundle

## Planned package structure

- library crate for artifact types, capture, and diff logic
- cargo subcommand for workspace execution and bundling
- optional adapters for `pin-init`, `moveit`, and Crubit `Ctor`

## Adoption sequence

### MVP
- manual profile file
- placement-topology receipt
- address-commit receipt
- failure-cleanup report
- bundle writer

### v0.2
- constructor-lane report
- transition diff
- CI helpers
- field-embedding scenarios

### v1
- adapter pack for `pin-init`, `moveit`, and Crubit
- richer async/caller-storage scenarios
- interop with unsafe-field and FFI lanes

## What this crate should explicitly refuse to do

- define the official Rust language design,
- collapse `moveit`, `pin-init`, and Crubit into one lane,
- infer full cleanup correctness from one green run,
- or promise soundness from a small casebook.
