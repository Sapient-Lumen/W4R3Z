# Sanitizer scope

The GCC 14 Debug ASan/UBSan lane builds and runs eight focused replica
executables: network model, hash-graph projection, allocation atomicity,
aggregate budget, capacity backpressure, outbox time fence, outbox lease, and
SQLite owner. The new time-fence library and test, changed lease and owner
translation units and tests, and bundled SQLite 3.53.3 compile with
`-fsanitize=address,undefined` and `-fno-omit-frame-pointer`; the focused
executables link the sanitizer runtime. Runtime enables leak detection and
halt-on-error behavior. Ninja command proof is retained verbatim.

This is not a full-project sanitizer, ThreadSanitizer, physical power-loss,
platform-portability, Release-mode all-target, or formal-proof claim.
