# Sanitizer scope

The GCC 14 Debug ASan/UBSan lane builds and runs the seven focused replica
executables: network model, hash-graph projection, allocation atomicity,
aggregate budget, capacity backpressure, outbox lease, and SQLite owner. The
changed lease and owner production translation units, their tests, and bundled
SQLite 3.53.3 compile with `-fsanitize=address,undefined` and
`-fno-omit-frame-pointer`; focused executables link the sanitizer runtime.
Runtime enables leak detection and halt/abort on sanitizer error.

This is not a full-project sanitizer claim, ThreadSanitizer claim, physical
power-loss test, or proof over platform/toolchain combinations not executed.
