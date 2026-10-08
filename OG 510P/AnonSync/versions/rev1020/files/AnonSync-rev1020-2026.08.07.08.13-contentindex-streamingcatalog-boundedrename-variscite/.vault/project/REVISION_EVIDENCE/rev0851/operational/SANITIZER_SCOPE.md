# Rev0851 sanitizer scope

The sanitizer lane used GCC 14.2 with
`-fsanitize=address,undefined`, leak detection, and halt-on-error behavior.
Emitted Ninja commands were inspected to confirm both compile and link flags.

The lane built and ran seven focused targets covering the new owned policy,
raw authorizer owner, integrated connection authority, transaction exception
composition, allocator-fault cutpoints, process/fork authority, and peer-ingress
schema authority. Result: **982/982** checks.

The bundled SQLite translation unit is intentionally excluded from sanitizer
instrumentation by the current build. This is focused coverage, not a
full-project sanitizer claim. ThreadSanitizer, MemorySanitizer, Windows, and
Release-mode sanitizer behavior were not tested.
