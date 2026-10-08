# rev0844 sanitizer scope

The final-source sanitizer lane used GCC 14.2 with AddressSanitizer and
UndefinedBehaviorSanitizer enabled, `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
and `UBSAN_OPTIONS=halt_on_error=1`.

It built and executed the four local JSONL publication/namespace/backend/crash
executables plus six integrated replay-ledger selftests: **10/10** passed.

This is a focused changed-boundary claim. It is not a full-project sanitizer
claim, not a thread-sanitizer claim, and not a storage fault-injection claim.
