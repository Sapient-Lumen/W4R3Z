# Sanitizer scope

The rev0860 sanitizer lane uses GCC 14.2 with
`-fsanitize=address,undefined -fno-omit-frame-pointer`,
`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`, and
`UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1`.

Instrumented C++ scope includes the extracted manifest-subset owner, its focused
corpus, and the C++ support libraries linked into that executable. Compile and
final link commands are retained in validation evidence. The focused corpus
passes 34/34 once and 25/25 repeated processes (850 observations).

The bundled SQLite amalgamation is C and is not instrumented by the project's
C++ sanitizer option. No full-project, ThreadSanitizer, Release-mode, Windows,
or hostile-allocation-fault sanitizer claim is made.
