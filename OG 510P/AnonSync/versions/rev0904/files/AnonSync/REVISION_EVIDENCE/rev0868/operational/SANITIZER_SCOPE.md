# Sanitizer scope: AnonSync rev0868

The rev0868 sanitizer lane is deliberately focused on the five replica-model
executables changed or directly relied upon by this revision:

- `anonsync_sync_replica_network_model_test`
- `anonsync_sync_replica_hash_graph_projection_test`
- `anonsync_sync_replica_allocation_atomicity_test`
- `anonsync_sync_replica_aggregate_budget_test`
- `anonsync_sync_replica_capacity_backpressure_test`

They are built with GCC AddressSanitizer and UndefinedBehaviorSanitizer,
frame-pointer preservation, leak detection, and halt-on-error. Compile and link
commands are separately inspected for the requested flags.

This is not full-project sanitizer coverage. The bundled SQLite C amalgamation,
the integrated core/domain executable, ThreadSanitizer, Windows, and all
production transport/filesystem paths are outside the claimed scope.
