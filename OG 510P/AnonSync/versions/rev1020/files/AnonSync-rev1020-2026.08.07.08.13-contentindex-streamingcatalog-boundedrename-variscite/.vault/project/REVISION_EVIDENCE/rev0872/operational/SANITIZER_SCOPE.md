# Sanitizer scope

The GCC 14 Debug ASan/UBSan lane builds and runs seven focused replica
executables: network model, hash-graph projection, allocation atomicity,
aggregate budget, capacity backpressure, outbox lease, and SQLite owner. The
changed lease and owner translation units, both tests, and bundled SQLite
3.53.3 compile with `-fsanitize=address,undefined` and
`-fno-omit-frame-pointer`; the focused executables link the sanitizer runtime.
Runtime sets leak detection and halt-on-error behavior. The command proof is
captured verbatim from Ninja.

This is not a full-project sanitizer, ThreadSanitizer, physical power-loss,
platform-portability, or formal-proof claim.
