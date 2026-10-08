# Unsafe Contract Auditor Kit fixtures

This fixture family exists to keep **P-0120 Unsafe Contract Auditor Kit** concrete.

The core claim is that unsafe review needs a **reviewable obligation-and-evidence contract**, not just prose, passing Miri output, or hand-wavy “unsafe checked” badges.

## Core review objects

- `contract-authority.receipt.json`
- `obligation-map.report.json`
- `interpreter-boundary.receipt.json`
- `witness-fidelity.report.json`
- `unsafe-audit-bundle.manifest.json`
- `authority-import.receipt.json`
- `obligation-drift.diff.json`
- `witness-comparison.report.json`

## What these fixtures are trying to protect

They protect against flattening all of the following into one fake verdict:

- where unsafe obligations came from,
- what unsafe sites actually exist,
- what a witness really observed,
- what the witness definitely did not observe,
- and whether the exported audit bundle is strong, advisory, or manual-review-heavy.

## Scenario families

### `miri_passes_but_ffi_boundary_stays_out_of_scope/`
A passing Miri run can still leave foreign behavior out of scope.
The fixture keeps that scope boundary visible.

### `docs_contain_safety_sections_but_no_machine_contract_authority/`
Helpful prose is still different from structured contract authority.
The fixture keeps authority-source truth explicit.

### `unsafe_attribute_obligation_is_symbol_contract_not_memory_model/`
Some unsafe obligations are about symbols or ABI truth, not aliasing or initialization.
The fixture keeps those obligation classes from being flattened into memory-model claims.

### `loom_schedule_witness_does_not_cover_aliasing_or_init/`
Concurrency schedule exploration is useful but not interchangeable with memory-model witnesses.
The fixture keeps witness fidelity honest.


### `std_contract_import_upgrades_authority_but_local_wrapper_keeps_manual_gap/`
Imported machine authority can strengthen the review story without fully closing local wrapper obligations.
The fixture keeps authority exactness and remaining manual gaps visible.

### `refactor_moves_unsafe_sites_without_closing_obligations/`
Unsafe sites can move or split during refactors without automatically changing the semantic obligation.
The fixture keeps site motion separate from semantic drift.

### `same_miri_pass_but_toolchain_or_target_shift_breaks_direct_comparison/`
Two green witness runs are not automatically comparable.
The fixture keeps target/toolchain/scope shifts from becoming fake “no change” stories.

### `ffi_callback_round_trip_keeps_boundary_partial_despite_green_run/`
A local callback harness can go green while foreign-side behavior stays only partially observed.
The fixture keeps callback/FFI boundary honesty explicit.
