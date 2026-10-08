# Publication rights gate ledger/root-rights boundary — rev0850

- Status: `passed_after_targeted_validation_pending_full_canonical_gate`
- Validator: `scripts/validate_publication_rights_gate_ledger_root_rights_boundary_rev0850.py`

## Purpose

Reject publication-rights decisions that depend on symlinked or non-regular publication-critical rights inputs. Earlier rev0845/rev0846 work closed symlink boundaries for referenced local license targets; rev0850 applies the same fail-closed rule to the rights ledger itself and to root `LICENSE`, `COPYING`, and `NOTICE` sentinels.

## Changed surfaces

- `scripts/publication_rights_gate.py`
- `scripts/validate_publication_rights_gate_ledger_root_rights_boundary_rev0850.py`

## Validator cases

- regular ready ledger plus regular root `LICENSE` passes validator probe
- symlinked `RIGHTS/component_license_ledger.json` blocks as `rights_ledger_load_error`
- symlinked `RIGHTS/` directory blocks before ledger read
- symlinked root `LICENSE` blocks even when the ledger is otherwise ready
- non-regular root `LICENSE` directory blocks

## Publication status

Publication remains blocked. This change does not declare or infer any license terms.
