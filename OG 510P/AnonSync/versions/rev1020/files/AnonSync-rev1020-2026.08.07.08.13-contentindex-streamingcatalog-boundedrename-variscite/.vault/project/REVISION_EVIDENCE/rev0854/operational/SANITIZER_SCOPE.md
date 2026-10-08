# Rev0854 sanitizer scope

The focused sanitizer lane used GCC 14.2 with
`-fsanitize=address,undefined`, frame pointers, leak detection, and
halt-on-error behavior. Generated Ninja rules were captured to prove sanitizer
flags on the affected C++ compilation and executable link steps.

Six focused executables passed **455/455** checks. They cover the extracted
SQLite database-mutex guard, busy-handler owner, verification budget,
authorizer owner, exact connection authority, and inherited-process authority.
The simultaneous duplicate-owner oracles execute under ASan+UBSan as part of
those suites.

The bundled SQLite 3.53.3 C translation unit was deliberately not instrumented,
matching the project's focused boundary. This is not a full-project sanitizer
claim. ThreadSanitizer, MemorySanitizer, Release-mode sanitizers, Windows,
arbitrary concurrent close/use, and foreign raw SQLite API replacement remain
outside this lane.
