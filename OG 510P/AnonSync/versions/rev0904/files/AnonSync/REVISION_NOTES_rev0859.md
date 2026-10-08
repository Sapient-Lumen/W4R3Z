# AnonSync rev0859

## Mission increment

Rev0858 proved that a fully materialized typed manifest could not force
unbounded post-validation traversal. Rev0859 moves the same resource policy to
the persistence reconstruction boundary so nested ownership cannot grow before
declared shape and row semantics become authorized.

## Severe defect corrected: validation followed partial allocation

Two production checkpoint readers independently reconstructed complete
`SyncManifestEntry` values. Each queried all chunk and lineage rows, appended
them to vectors, and only afterward called the typed validator and compared
stored digests. Recorded `chunk_count` and `lineage_count` values were available
in the parent row but did not control growth.

A hostile or corrupt checkpoint could therefore cause principal-process memory
and traversal amplification before rejection. The duplicate implementations
also made it easy for count, ordering, digest, and output-commit behavior to
drift.

## Frozen incremental owner

`SyncManifestEntryStreamDecoder` is a single-use state machine:

1. `begin()` admits one entry, both declared row counts, path bytes, scalar
   metadata bytes, and header semantics before retaining the header.
2. `append_chunk()` rejects excess rows, noncontiguous ranges, zero lengths,
   malformed hashes, and offset overflow before budget admission and copy.
3. `append_lineage()` rejects excess rows, invalid identifiers, zero counters,
   duplicates, and disorder before budget admission and copy.
4. `finish()` requires exact counts and exact file coverage, reruns independent
   typed validation, compares independently computed resource usage, and only
   then moves the candidate into output.

Any ordinary validation failure is sticky. The first cause is retained, the
partial candidate is destroyed, accepted-row counters are reset, and later
operations cannot reactivate the owner. No declared count is passed to
`vector::reserve()`.

## SQLite boundary refactor

Both complete entry reloaders now:

- select recorded chunk and lineage counts with the scalar parent row;
- read those counts before bounded text ownership;
- cap IDs at 128 bytes, paths at 4096 bytes, SHA-256 text at 64 bytes, and entry
  kind text at 9 bytes;
- feed rows only to the streamed owner;
- reject the first extra row before nested vector growth;
- require exact missing-row detection at finish; and
- publish externally only after stored entry and version digests round-trip.

The SQLite support layer now exposes a bounded exact-text overload backed by the
existing exact-value decoder. `is_lowercase_sha256_hex()` now accepts
`std::string_view`, so syntax checks do not require ownership conversion.

## Audit/refactor result

The two former full-entry loaders contain zero direct nested-vector pushes.
Resource accounting is shared with typed validation instead of reimplemented.
The owner is a separate invariant-owned CMake target, linked by the core and
listed in sanitizer compile/link inventories.

The new registered source audit passes 32/32 checks and verifies code ordering,
not merely symbol presence. It requires count admission before scalar retention,
row count and byte admission before vector growth, semantic checks before copy,
independent validation before output, bounded SQLite reads in both loaders, no
`reserve()`, no stream-locale formatting, and revision-scoped release packaging.

## Validation result

- GCC 14.2 Debug: complete 294-action all-target graph and true zero-work final
  dependency closure.
- CTest: 158/158 in exact ranges 1-50, 51-72, 73-100, and 101-158.
- Registered structural audits: 47/47.
- New stream-decoder audit: 32/32.
- GCC Debug, Clang 17 `-Werror`, and GCC ASan+UBSan focused runtime: 761/761
  checks in every lane.
- Repeatability: 100 normal rounds and 25 instrumented rounds of both focused
  owner executables, totaling 250/250 process runs and 13,500 check
  observations.
- Parent archive: rev0858 independently verifies at 26/26 ZIP and 22/22
  directory checks; SHA-256
  `8329be71fdcfd683c9d1f13b4ce54585a5899df9d0eb85e322689b1f10d161ca`.
- Source patch: 14 active files, 1,614 insertions, 150 deletions; exact replay
  across all 303 active files.

## Deliberate limits

The owner covers complete manifest-entry reconstruction, not every specialized
query that consumes only chunk subsets for scheduling, receipts, repair, or
execution. Those paths need narrower purpose-specific row budgets rather than a
blind reuse of a complete-entry type.

Scalar SQLite fields are individually bounded, but wire/persistence decoding is
not globally allocation-bounded. No single uninterrupted 158-test invocation
is claimed; four exact non-overlapping final-source ranges are the complete
gate. No full-project sanitizer, ThreadSanitizer, Release-mode all-target,
Windows runtime, distributed convergence, confidentiality, anonymity, or
hostile-worker-isolation claim is made.
