# Proof obligation — rev0056

Required local proof lane:

```text
pytest tests/test_rev0056_recovery_cleanup_chaosbudget.py
python3 scripts/evidence/check_surfaces.py
python3 scripts/evidence/run_micro_simulation.py
python3 scripts/evidence/run_compile_check.py
python3 scripts/evidence/run_cube_audit.py
```

Obligation: show that accepted effect seal is not enough for post-restart cleanup or further chaos work; recovery mesh, safe cleanup, and chaos budget each must bind to the same exact boundary.
