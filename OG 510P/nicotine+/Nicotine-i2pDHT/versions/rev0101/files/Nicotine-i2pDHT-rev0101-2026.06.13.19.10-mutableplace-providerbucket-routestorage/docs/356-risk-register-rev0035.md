# Risk register — rev0035

| Risk | Current pressure test |
|---|---|
| Launch profile drift | `startmatrix.py` binds profile to launch-intent digest. |
| I2P-only fallback drift | I2P-only + classic fallback is quarantined. |
| Bundle config mistakes | `routerharness.py` checks persistence, proxies, notransit, endpoint drift. |
| External SAM confusion | External endpoints require explicit allowance and endpoint match. |
| Diagnostics as side channel | `telemetrydebt.py` treats retained metrics as budgeted local state. |
| Evidence loss via telemetry compaction | hard-negative summaries require hard evidence retained by evidence GC. |
| Audit sprawl | `startfold.py` and revision-aware `foldmap.py` pin current navigation. |
