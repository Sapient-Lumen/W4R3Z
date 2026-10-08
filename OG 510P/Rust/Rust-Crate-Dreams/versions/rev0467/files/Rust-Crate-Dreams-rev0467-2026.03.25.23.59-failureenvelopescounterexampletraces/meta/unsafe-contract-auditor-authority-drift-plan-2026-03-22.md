# Unsafe Contract Auditor authority/drift/comparison plan — 2026-03-22

This note deepens **P-0120 Unsafe Contract Auditor Kit** around one product question:

> what should another engineer receive when unsafe obligations, authority sources, or witness meaning change across revisions?

## Main judgment

`0.2` for **P-0120** should stop treating “unsafe inventory + witness run” as the end of the story.
It should add **authority imports**, **obligation drift**, and **witness comparison** as first-class review objects.

That is the smallest next step that makes the crate useful in release review, downstream assurance review, and refactor review.

## Why these review objects matter

### 1. Authority imports
Unsafe obligations increasingly have multiple plausible sources:
- handwritten `# Safety` docs,
- future contract attributes,
- std-contract imports,
- imported upstream manifests,
- and local manual declarations.

A worthy crate should never flatten those into one fake “authoritative contract exists” answer.

### 2. Obligation drift
Unsafe posture changes are often subtle.
A refactor can:
- move unsafe sites without changing the obligation,
- split one site into three sites while keeping the same semantic contract,
- or silently introduce a new callback/symbol/init obligation.

Reviewers need a diff object that keeps **site movement** separate from **semantic obligation changes**.

### 3. Witness comparison
A green witness result is not stable evidence unless its meaning is stable.
Two passing runs may still fail to be honestly comparable because:
- the target changed,
- the toolchain changed,
- the witness scope changed,
- non-claims changed,
- or an FFI boundary stayed partially out of scope.

## Recommended new artifacts

### `authority-import.receipt.json`
Records imported authority sources and how they were normalized.
It should say:
- source kind,
- upstream location,
- obligations covered,
- exactness class,
- freshness/tool version,
- conflicts with local declarations,
- and whether manual review is still required.

### `obligation-drift.diff.json`
Compares unsafe obligation posture between two revisions.
It should separate:
- added obligations,
- removed obligations,
- site moves,
- obligation-class changes,
- unresolved-gap changes,
- and witness-linkage changes.

### `witness-comparison.report.json`
Compares two witness results only when comparison is honest.
It should say:
- which witnesses were compared,
- whether comparison is valid,
- what claim scope changed,
- whether evidence strength changed,
- and what manual review is still required.

## CLI refinement

### `cargo unsafe-audit import-authority`
Import docs / std-contract / upstream authority into normalized receipts without claiming perfect equivalence.

### `cargo unsafe-audit diff old/ new/`
Should now emit both:
- `obligation-drift.diff.json`
- and any `witness-comparison.report.json` objects that are valid to compute.

### `cargo unsafe-audit doctor`
Should render warnings such as:
- `authority_import_exactness_dropped`
- `unsafe_site_count_changed_without_semantic_mapping`
- `witness_scope_shift_breaks_comparison`
- `ffi_callback_boundary_still_partial`
- `imported_contract_conflicts_with_local_manifest`

## Boundary clarifications

### Not the std-contracts goal itself
The std-contracts goal creates substrate for machine-readable contracts.
P-0120 imports that substrate into a crate-facing review workflow.

### Not the unsafe-fields language feature
Unsafe fields mark where safety invariants live.
P-0120 still owns the audit artifact that explains how those invariants were reviewed and witnessed.

### Not a proof engine
Even with richer imports and comparisons, P-0120 must still refuse to imply full soundness.
Its job is **honest transportable review state**, not proof.

## Recommended `0.2` scenario set

1. `std_contract_import_upgrades_authority_but_local_wrapper_keeps_manual_gap/`
2. `refactor_moves_unsafe_sites_without_closing_obligations/`
3. `same_miri_pass_but_toolchain_or_target_shift_breaks_direct_comparison/`
4. `ffi_callback_round_trip_keeps_boundary_partial_despite_green_run/`

## What this crate should provide other people after this pass

1. **One normalized authority import trail**.
2. **One semantic unsafe-obligation diff**.
3. **One witness-comparison verdict**.
4. **One explicit boundary receipt for partial callback/FFI scope**.
5. **One portable audit bundle that survives review handoff**.
