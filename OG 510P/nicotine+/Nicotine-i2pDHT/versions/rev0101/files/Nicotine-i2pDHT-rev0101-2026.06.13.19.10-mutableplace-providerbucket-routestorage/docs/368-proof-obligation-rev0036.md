# Proof obligation — rev0036

The rev0036 proof obligation is local and narrow:

- Service catalogs must reject bad signatures, replay, sequence rollback/fork, binding drift, bridge drift, time-window failure, and capacity overclaim.
- Load sheaths must keep protected service work from starving, bound useful refusals, reject replayed windows, and enforce metadata budgets.
- Profile GC must preserve active profile/router memory and hard negatives while allowing soft compaction.
- Foldregistry/servicefold must expose rev0036 code, tests, and docs through public surface, head registry, docs index, surface ledger, and predecessor fold checks.

Required evidence:

```text
tests/test_rev0036_servicecatalog_loadsheath_profilegc.py
scripts/evidence/check_surfaces.py
scripts/evidence/run_micro_simulation.py
scripts/evidence/run_compile_check.py
scripts/evidence/run_cube_audit.py
```
