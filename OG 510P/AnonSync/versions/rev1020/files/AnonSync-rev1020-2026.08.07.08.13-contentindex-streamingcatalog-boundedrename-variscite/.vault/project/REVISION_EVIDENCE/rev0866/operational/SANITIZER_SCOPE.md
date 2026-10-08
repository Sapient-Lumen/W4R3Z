# Rev0866 sanitizer scope

The sanitizer claim is intentionally focused. GCC 14 AddressSanitizer and
UndefinedBehaviorSanitizer instrument the canonical codec, pure evidence
projector, replica model, network simulator, SHA-256/conflict/manifest support,
and the three focused executables:

- `anonsync_sync_replica_network_model_test`
- `anonsync_sync_replica_hash_graph_projection_test`
- `anonsync_sync_replica_allocation_atomicity_test`

`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1:abort_on_error=1` and
`UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1` are used. All three registered
focused tests pass. Ninja command inspection proves `-fsanitize=address,undefined`
on 10/10 relevant C++ compile commands and 3/3 executable link commands.

The graph stress corpus reaches roughly 759 MiB resident under ASan because the
instrumented global reprojection oracle deliberately retains and repeatedly
reconstructs complete graph metadata. This is not a production memory claim.

No claim is made for the integrated `anonsync_core`, the bundled SQLite C
amalgamation, every repository target, ThreadSanitizer, Release mode, Windows,
or real multi-process transport under sanitizers.
