# AnonSync rev0789 — row-state truth, alias-proof evidence, and focused build graph

Prepared from the supplied, verified rev0788 archive. The immediate parent ZIP
has SHA-256 `02b1d020667224fa167c4dab705f933d59c8770f194db322ad64e6698cfdee7d` and passes all 24 checks in the rev0789 release-package
verifier, including a recomputation of rev0788's legacy active projection.

## Mission

AnonSync's heart is not “copy bytes until two folders look alike.” It is to make
convergence explainable and reconstructible: each transition must be authorized
by evidence specific to the boundary that owns it. Transport success is not
acceptance, a database address is not lifetime authority, a row-shaped API is
not a current row, and equal values are not independent evidence for two fields.

## Severe defects corrected

### Undefined SQLite row access

`SqliteProjectionDecoder::decode()` accepted a non-null prepared statement and
immediately invoked `sqlite3_column_count()`, `sqlite3_column_type()`, and other
column APIs. It did not prove that the statement currently pointed at a result
row. SQLite defines column access as undefined unless the most recent
`sqlite3_step()` returned `SQLITE_ROW` and no reset/finalize followed.

The decoder now requires a positive projection column count and
`sqlite3_data_count(statement) == sqlite3_column_count(statement)` before any
column-value API. Prepared-but-unstepped, exhausted, and reset statements fail
closed as `statement_not_positioned`.

### Evidence aliasing through duplicate column maps

The twelve-field `ProjectionColumnMap` checked only range. A caller could map two
fields to one result column. The preserved rev0788 reproducer maps
`transport_key_id` to the `transport_instance_id` column, omits the actual key
column, and still passes canonical verification when the two expected strings
are equal. Pre-fix output records
`forged_omitted_column_verified=true`.

Rev0789 preflights the complete map and rejects the second repeated index as
`duplicate_column_index`. One stored value may not be laundered into two pieces
of evidence, even when their canonical values happen to match.

### TEXT extraction and empty values

The decoder now calls `sqlite3_column_text()` before `sqlite3_column_bytes()`,
uses SQLite's documented safe extraction order, distinguishes an empty TEXT
value from allocation failure, and has a direct empty-string regression test.

## Architecture correction

The rev0788 connection-profile “focused” test linked `anonsync_core_lib`, which
forced 40 Ninja actions, 34 first-party C++ translation units, 26 core units, and
52,607 first-party lines—including the 24,530-line domain—into an 85-check proof
for a 267-line boundary.

Rev0789 creates independently linkable libraries for the connection profile,
canonical projection verifier, and SQLite projection decoder. Production core
links them privately; focused tests link only their boundary. Configure-time
assertions reject source reabsorption or reverse dependencies on the core.

Measured from fresh Ninja graphs:

| Focused target | Before actions | After | Before C++ lines | After | Core TUs after |
|---|---:|---:|---:|---:|---:|
| connection profile | 40 | 6 | 52,607 | 564 | 0 |
| canonical verifier | 40 | 4 | 52,549 | 396 | 0 |
| SQLite decoder | 40 | 8 | 52,615 | 850 | 0 |

This is correctness infrastructure: cheap boundary proofs make sanitizer,
strict-compiler, mutation, and fuzz lanes practical instead of ceremonial.

## Real fuzzing

`fuzz/fuzz_sqlite_projection_decoder.cpp` implements
`LLVMFuzzerTestOneInput` and mutates statement state, twelve SQLite binding
classes/values, valid and malformed permutations, duplicate/out-of-range maps,
embedded bytes, and error-summary invariants. The target directly instruments
the two small persistence implementations. A 100,000-run Clang libFuzzer/UBSan
campaign completed with coverage 344, feature count 736, and no crash or
sanitizer finding.

The three pre-existing `anonsync_fuzz_*` executables are deterministic selftests,
not coverage-guided engines; CMake now says so explicitly.

## Release-truth correction

The legacy active implementation projection excluded `fuzz/`. The manifest did
bind those files, but the named “tested active projection” did not. Rev0789
introduces `anonsync-active-implementation-projection-v2`, includes all fuzz
sources, and changes `tools/verify_release_package.py` to recompute the exact
file list, per-file hashes, byte count, and aggregate digest. The current v2
digest is `c6128ec0f2156922a56badc6170122de6957eb0132581a6b045e460103d78882`.

## Validation

- full GCC Debug build and 44/44 CTest;
- focused Debug 20/20 for all three boundaries;
- GCC ASan/UBSan 5/5;
- Clang 17 strict C++20/Werror 5/5;
- GCC 14 `-O3 -DNDEBUG -Werror` 5/5;
- libFuzzer/UBSan 100,000 runs;
- all seven deterministic authority audits pass;
- parent rev0788 package verification 24/24 with the revised verifier.

## Explicitly unresolved

No fault-injecting VFS crash matrix, native descriptor identity attestation,
media-durability proof, formal convergence model, end-to-end content encryption,
metadata-privacy model, or secret-memory lifecycle is claimed. The default
sanitizer lane instruments AnonSync C++ but not the pinned SQLite amalgamation.
This cloudtainer's Swift Clang 17 libFuzzer runtime runs with UBSan and
`-print_funcs=0`; its function-symbolization path and ASan-combined startup are
recorded as toolchain limitations rather than passed gates.
