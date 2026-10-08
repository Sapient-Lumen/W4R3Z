# Sanitizer scope

The rev0861 sanitizer lane uses GCC 14.2 with
`-fsanitize=address,undefined -fno-omit-frame-pointer`,
`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1:abort_on_error=1`, and
`UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1`.

Instrumented C++ scope includes the extracted claimed-path snapshot owner, its
27-check corpus, the integrated peer-ingestion implementation, the core, and the
607-check domain-model selftest. Compile and final-link commands for the focused
owner and integrated core are retained in validation evidence. Both selected
runtimes pass, and the focused corpus passes 25/25 repeated processes (675
observations).

The bundled SQLite amalgamation is C and is deliberately built without the
project's C++ sanitizer option. The lane is therefore a selected C++ boundary
and integration check, not a full-project or fully instrumented dependency
claim. No ThreadSanitizer, Release-mode, Windows, hostile-allocation-fault, or
complete registered-test sanitizer claim is made.
