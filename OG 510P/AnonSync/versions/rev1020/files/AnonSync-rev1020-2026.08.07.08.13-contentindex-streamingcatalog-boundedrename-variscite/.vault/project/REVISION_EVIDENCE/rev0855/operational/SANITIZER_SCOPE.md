# Rev0855 sanitizer scope

The sanitizer lane used GCC 14.2 with
`ANONSYNC_ENABLE_SANITIZERS=ON`, AddressSanitizer,
UndefinedBehaviorSanitizer, frame pointers, leak detection, and halt-on-error.
Generated Ninja commands were inspected independently for
`-fsanitize=address,undefined` on compile and link steps.

Six focused executables passed **461/461** checks:

- SQLite busy-handler owner;
- SQLite verification budget;
- SQLite authorizer owner;
- SQLite support and scoped-mutation guards;
- SQLite connection authority; and
- SQLite process-authority fork tests.

Bundled SQLite's C amalgamation was not sanitizer-instrumented. This is not a
full-project sanitizer, ThreadSanitizer, Release-mode, Windows, or arbitrary
concurrent teardown claim.
