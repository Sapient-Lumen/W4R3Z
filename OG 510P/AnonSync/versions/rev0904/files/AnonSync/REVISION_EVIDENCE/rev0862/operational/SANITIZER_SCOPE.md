# Sanitizer scope

GCC 14.2 ASan+UBSan (`address,undefined`) compiled and linked the focused
sidecar execution-budget target and the integrated `anonsync_core` target with
frame pointers. Runtime used leak detection and halt-on-first-error.

Executed:

- focused sidecar snapshot corpus: 35/35;
- integrated sync-domain corpus: 609/609;
- focused repeatability: 25/25 processes, 875 checks.

The generated Ninja command inventory proves sanitizer compile and link flags
for the C++ targets. The bundled SQLite C amalgamation is linked into these
executables but is not compiled with the C++ sanitizer option. This is not a
full all-target sanitizer claim and does not include ThreadSanitizer.
