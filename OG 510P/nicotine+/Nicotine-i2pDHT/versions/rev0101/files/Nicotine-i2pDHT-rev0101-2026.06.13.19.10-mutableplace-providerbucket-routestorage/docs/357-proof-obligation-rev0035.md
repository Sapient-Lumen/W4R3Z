# Proof obligation — rev0035

rev0035 must demonstrate locally that:

1. router harness decisions reject ephemeral destinations, proxy exposure, bundle `notransit`, replay, config mismatch, endpoint drift, and unapproved session-only proof;
2. start profile decisions accept leaf/garden/bridge/offline profiles only when their mode-specific preconditions bind to the launch quorum and router harness;
3. I2P-only mode cannot silently enable classic fallback;
4. telemetry retention rejects raw leaks, scope mixing, cardinality overrun, byte debt, and hard-negative evidence loss;
5. `startfold.py` sees the rev0035 surface and the rev0034 predecessor fold.

Evidence:

```text
tests/test_rev0035_startmatrix_telemetry_router.py
scripts/evidence/check_surfaces.py
scripts/evidence/run_micro_simulation.py
scripts/evidence/run_compile_check.py
scripts/evidence/run_cube_audit.py
```
