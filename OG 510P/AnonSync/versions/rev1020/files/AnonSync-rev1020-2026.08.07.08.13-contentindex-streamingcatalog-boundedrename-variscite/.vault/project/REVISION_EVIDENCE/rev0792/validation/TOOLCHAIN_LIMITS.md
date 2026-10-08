# Validation limits

The pure schema owner completed GCC ASan/UBSan five times. The integrated
sanitizer target began compiling first-party dependencies but did not finish the
large core archive within the execution window; no integrated sanitizer runtime
claim is made. The bundled SQLite amalgamation was intentionally left
uninstrumented in the focused first-party sanitizer lane.

`clang-format` 14 was observed earlier in the session but was no longer
available when the final tree was frozen. New C++ was checked by GCC 14 and
Clang 17 strict warning profiles, `git diff --check`, direct focused/integrated
execution, and the complete Debug suite; no final clang-format claim is made.

Exact version-10 schema identity is a fail-closed compatibility rule. Databases
with semantically equivalent formatting, explicit SQLite statistics objects, or
local schema alterations are rejected. No automatic migration is provided.

Total untrusted snapshot file size, page count, row count, virtual-machine work,
wall time, cache/heap, and allocation volume remain incompletely bounded.
