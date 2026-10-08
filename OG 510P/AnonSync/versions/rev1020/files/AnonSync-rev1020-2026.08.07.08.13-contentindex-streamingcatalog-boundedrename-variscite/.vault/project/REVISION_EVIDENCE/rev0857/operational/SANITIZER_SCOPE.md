# Sanitizer scope

GCC 14.2 built and ran the four focused policy/identity executables plus the
integrated sync-domain model with AddressSanitizer and UndefinedBehaviorSanitizer.
Runtime options enabled leak detection and halt/abort on first error. The lane
passed **694/694** checks.

The first attempt exposed a real CMake defect: the two new tests were listed for
sanitizer compilation but not for sanitizer final linking, producing undefined
ASan/UBSan runtime symbols. That failed log is retained as operational evidence.
The final CMake graph adds both executables to the sanitizer link inventory, and
the source audit now checks compile and link lists separately.

Generated Ninja commands prove `-fsanitize=address,undefined` on the new owner
and test compile commands and on both final executable links. The bundled SQLite
C amalgamation was not instrumented. No full-project sanitizer,
ThreadSanitizer, Release-mode, or Windows-runtime claim is made.
