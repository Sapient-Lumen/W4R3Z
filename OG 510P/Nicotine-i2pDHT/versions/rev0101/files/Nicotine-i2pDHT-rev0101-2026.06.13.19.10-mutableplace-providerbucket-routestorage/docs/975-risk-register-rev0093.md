# Risk register rev0093

| Risk | Current pressure |
|---|---|
| Loopback mistaken for native load permission | `nativeloadloop` accepts only held loopback and forbids load/dispatch. |
| Python result canary mistaken for native result parity | `nativecallcanary` rejects native result and native execution. |
| Dispatch fence mistaken for dispatch release | `dispatchfence` accepts only fenced state. |
| Memory drops across native branch lanes | all three rev0093 lanes require tombstone/fallback/quarantine/crash memory preservation. |
| One-family evidence laundering native readiness | all three lanes require family and path-family diversity. |
| Native branch audit sprawl | `nativefoldspine` and `nativeloadloopfold` pin the current branch. |
