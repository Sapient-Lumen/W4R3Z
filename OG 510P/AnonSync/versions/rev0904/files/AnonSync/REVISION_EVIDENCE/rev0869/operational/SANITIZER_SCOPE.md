# Sanitizer scope: AnonSync rev0869

The GCC ASan/UBSan lane is focused on the six replica executables changed or
directly relied upon by rev0869:

- `anonsync_sync_replica_network_model_test`
- `anonsync_sync_replica_hash_graph_projection_test`
- `anonsync_sync_replica_allocation_atomicity_test`
- `anonsync_sync_replica_aggregate_budget_test`
- `anonsync_sync_replica_capacity_backpressure_test`
- `anonsync_sync_replica_sqlite_owner_test`

All six test translation units and executable links contain
`-fsanitize=address,undefined`; compile commands also contain
`-fno-omit-frame-pointer`. Runtime uses leak detection and halt-on-error through
the configured CTest environment. The bundled SQLite C amalgamation is
intentionally not instrumented by this lane.

This is not full-project sanitizer coverage. The integrated core/domain
executable, all production transport/filesystem paths, ThreadSanitizer, Windows,
and every historical target are outside the claimed scope.
