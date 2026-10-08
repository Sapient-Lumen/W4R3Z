# Rev0971 audit

## Defect corrected

The history owner accepted up to 1,024 entries and canonical paths up to 4,096
bytes, while the owner-only status socket rejected JSON responses above 1 MiB.
Because JSON escaping can expand one input byte into a six-byte `\u00XX` escape,
an accepted owner page could become unpublishable only after the owner had
completed it. The same completed page was also retained in both stable history
status and generic `last_step`, doubling its dominant memory and wire cost.

## C++ correction

Rev0971 adds one canonical streaming history JSON encoder used for exact byte
counting and final emission. The service retains the largest deterministic strict
prefix at or below 256 KiB, reports entry-count and byte frontiers independently,
and continues through the existing exact operation cursor and source cutpoint.
The completed inventory is retained once in `historical_versions.last_inventory`;
generic step status retains generation, request, action, and typed failure
correlation without another inventory. Status advances to v16.

## Adjacent refactor

Counting uses a custom stream buffer and never allocates the rejected output. The
shipping status renderer uses the stream form directly, avoiding another accepted-
inventory temporary. CLI frames, owner acceptance responses, exact/metadata
source tokens, restore semantics, and reconciliation generation 2 remain
unchanged.

## Mechanical evidence

- GCC 14.2 Debug graph: **528/528 edges**.
- GCC registry: **258/258 tests**.
- Independent GCC product lane: **39/39 tests**.
- Structural authority audit: **267/267 checks**.
- Clang 17 ASan/UBSan product graph: **239/239 edges**.
- Sanitizer product lane: **39/39 tests**, leak detection and halt-on-error.
- Focused sanitizer folder-owner proof: **406 checks**, 18.93 seconds,
  1,371,184 KiB peak RSS.
- Focused sanitizer local-control proof: **132 checks**, 0.57 seconds.
- Aggregate authoritative-log scan: no retained compiler, linker, sanitizer,
  runtime-error, or leak diagnostic.
- Exact parent verification: **41/41 checks**.
- Binary-aware reconstruction: **13/13 changed active files** plus the complete
  570-file projection.

## Nonclaims

This is a bounded diagnostics and recovery-browser correction. It is not history
retention policy, chronology, garbage collection, selective synchronization,
remote transfer of superseded operations, batch restore, directory restore, or
a global proof that arbitrary future status domains are bounded. The terminal
1 MiB socket guard remains fail closed.
