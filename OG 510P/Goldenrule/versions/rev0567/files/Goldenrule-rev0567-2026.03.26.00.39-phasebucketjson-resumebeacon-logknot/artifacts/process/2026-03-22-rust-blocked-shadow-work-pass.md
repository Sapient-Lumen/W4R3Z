# 2026-03-22 Rust-blocked shadow-work pass

## Boundary observed locally

- `make doctor` still fails only at missing `cargo` / `junest`.
- `make test-quick` still clears control tests and then stops only at `rust_lib_tests` because `tools/rust_exec.sh` cannot find JuNest.
- Python, Node, and GCC remain available in this cloudtainer.

## Durable additions from this pass

- `docs/RUST_SURFACE_INVENTORY.md`
- `artifacts/reports/rust_surface_inventory.json`
- `scripts/report/build_rust_surface_inventory.py`
- `docs/LIBRARY/topics/rust_blocked_cloudtainer_sessions_should_shift_to_static_surface_mapping_and_python_shadow_work.md`

## Why these were worth keeping

The archive needed one compact navigation object that future sessions can regenerate locally without a Rust toolchain. The new inventory records module boundaries, public surfaces, dependency waves, hotspot modules, and a reading order for `gr_engine` without pretending to provide runtime truth.

## Next implementor move

1. Regenerate the static Rust inventory at the start of any still-blocked session.
2. Spend blocked sessions on schema / report / Python-shadow work against declared contracts.
3. Keep runtime-semantic claims provisional until the Rust lane reruns on a machine with `cargo`.
4. Use remote Rust tools only for tiny self-contained snippets, not for broad archive externalization.
