# Rev0874 sanitizer and analyzer scope

## GCC ASan/UBSan

The GCC 14 Debug focused lane configured both
`ANONSYNC_ENABLE_SANITIZERS=ON` and
`ANONSYNC_SANITIZE_BUNDLED_SQLITE=ON`. Leak detection and halt-on-error were
enabled at runtime. The owned clock, lease, SQLite owner, tests, and bundled
SQLite C amalgamation were instrumented. All 265 focused checks passed.

This is not a full-project sanitizer claim. ThreadSanitizer, MemorySanitizer,
hardware power-loss behavior, and every legacy target were not covered by this
lane.

## Clang warnings

Clang 17 Release compiled the three focused C++ boundaries with `-Werror` and ran
all 265 checks. The bundled SQLite amalgamation was compiled as C by GCC in this
mixed-toolchain configuration; one amalgamation warning is therefore outside
the Clang C++ `-Werror` claim.

## Clang static analyzer

Default interprocedural analysis covered:

- `src/sync_replica_outbox_clock.cpp`
- `src/sync_replica_outbox_clock_linux.cpp`
- `src/sync_replica_outbox_lease.cpp`

The large `src/sync_replica_sqlite_owner.cpp` translation unit was analyzed with
an explicitly shallow/no-IPA configuration. All four scoped translation units
reported zero diagnostics. Default-interprocedural analysis of the owner and
analysis of test translation units are not claimed.
