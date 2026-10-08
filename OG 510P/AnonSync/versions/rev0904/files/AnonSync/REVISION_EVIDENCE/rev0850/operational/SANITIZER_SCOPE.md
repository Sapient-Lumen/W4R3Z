# AnonSync rev0850 sanitizer scope

The sanitizer lane uses GCC 14.2 with
`-fsanitize=address,undefined -fno-omit-frame-pointer`,
`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1:abort_on_error=1`, and
`UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1`.

Instrumented focused targets cover the new authorizer owner, retained callback
claim, integrated connection authority and transaction paths, process/fork
authority, and peer-ingress schema authority. The six direct runtime corpora
pass 950/950 checks with no AddressSanitizer, UndefinedBehaviorSanitizer, or
LeakSanitizer marker.

Bundled SQLite is deliberately not sanitizer-instrumented in this lane
(`ANONSYNC_SANITIZE_BUNDLED_SQLITE=OFF`). This is focused, not full-project,
coverage. ThreadSanitizer, MemorySanitizer, Windows sanitizers, and arbitrary
concurrent teardown are not claimed.
