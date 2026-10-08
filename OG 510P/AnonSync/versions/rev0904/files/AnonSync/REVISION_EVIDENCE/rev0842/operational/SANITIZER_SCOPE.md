# rev0842 sanitizer scope

GCC 14.2 AddressSanitizer and UndefinedBehaviorSanitizer were configured with leak
detection. The five exact extracted or changed leaves completed under the sanitizer
runtime:

- bounded regular-file reader: 15 checks;
- local JSONL replay publication: 31 checks;
- effect-transition intent publication: 34 checks;
- effect-transition durable record material: 20 checks;
- SQLite snapshot-manifest publication: 31 checks.

CTest reports **5/5** sanitizer targets passed. The focused leaves include the shared
publication primitives used by the refactored codecs.

A full-project sanitizer executable is not claimed. Compilation reached the monolithic
selftest owners but did not complete within the available command window. The result is
recorded as build/architecture debt, not represented as either a sanitizer pass or a
runtime failure. Non-leaf integration behavior is covered by the final GCC Debug and
Clang `-Werror` runs, not by a full sanitizer claim.
