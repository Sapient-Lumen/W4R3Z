# Rev0865 sanitizer scope

The sanitizer claim is intentionally focused on the new causal model, network
simulator, and the modified manifest conflict planner corpus.

GCC 14 configured with `ANONSYNC_ENABLE_SANITIZERS=ON` built and ran:

- `anonsync_sync_manifest_conflict_convergence_test`; and
- `anonsync_sync_replica_network_model_test`.

Runtime used leak detection and halt-on-error for AddressSanitizer plus
halt-on-error for UndefinedBehaviorSanitizer. Both registered focused tests
passed without sanitizer diagnostics.

Ninja command inspection proved `-fsanitize=address,undefined` on 5/5 selected
C++ compile commands and 2/2 executable link commands. The selected compilation
surface includes the model, simulator, their focused test, and the planner
integration dependencies needed by the conflict corpus.

No claim is made for full-project sanitizer coverage, integrated-core sanitizer
runtime, bundled SQLite C amalgamation instrumentation, ThreadSanitizer,
MemorySanitizer, allocator-failure coverage of every standard-library operation,
or repeatability beyond the recorded invocation.
