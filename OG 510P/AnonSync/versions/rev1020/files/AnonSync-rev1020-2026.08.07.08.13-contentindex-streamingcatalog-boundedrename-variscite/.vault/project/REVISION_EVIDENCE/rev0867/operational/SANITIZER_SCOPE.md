# Sanitizer scope

The GCC 14.2 RelWithDebInfo focused lane instruments the sync-replica model,
codec, projector, network simulator, their supporting SHA-256/conflict/path
libraries, and four focused executables with AddressSanitizer and
UndefinedBehaviorSanitizer. Eleven C++ compile commands contain
`-fsanitize=address,undefined -fno-omit-frame-pointer`; four executable link
commands contain `-fsanitize=address,undefined`.

Runtime uses:

- `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1:abort_on_error=1`
- `UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1`

All four focused executables pass 2,068 checks. This is not a full-project
sanitizer claim. The integrated CLI/domain runtime, bundled SQLite C
amalgamation, platform-specific backends, and ThreadSanitizer are outside this
lane.
