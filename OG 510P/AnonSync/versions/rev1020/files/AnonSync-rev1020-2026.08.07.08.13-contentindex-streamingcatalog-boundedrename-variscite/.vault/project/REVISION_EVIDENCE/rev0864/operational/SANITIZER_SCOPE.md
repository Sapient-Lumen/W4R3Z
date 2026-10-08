# Rev0864 sanitizer scope

The sanitizer claim is intentionally focused.

GCC 14 compiled the new digest-bound frame owner, its SHA-256 dependency, and
its focused test with `-fsanitize=address,undefined`; the focused executable link
also carries those sanitizers. The command proof records 3/3 C++ compile commands
and 1/1 link command instrumented.

Runtime used:

`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`

`UBSAN_OPTIONS=halt_on_error=1`

The 11-check focused corpus passed without sanitizer output.

No claim is made for an integrated-core sanitizer build, full-project sanitizer
coverage, bundled SQLite C instrumentation, ThreadSanitizer, or sanitizer
repeatability beyond this recorded invocation.
