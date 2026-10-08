# Bundled SQLite single-profile attestation audit — AnonSync rev0905

## Executive conclusion

AnonSync's local authority spine depends on SQLite for durable identity,
bootstrap, leases, membership, effects, replay state, and recovery evidence. The
engine was already pinned and the product runtime rejected the wrong linked
version, but rev0904 expressed that trust decision twice: CMake owned two file
hashes while C++ separately owned the version and source ID. Those independent
copies could drift. The build could then approve one set of bytes while the
runtime reported a different notion of the reviewed dependency.

Rev0905 replaces that split trust decision with one reviewed profile. The same
record selects the vendor directory, commits the upstream archive identity,
commits every retained vendor file, generates private C++ constants, statically
binds the included SQLite header, and drives the live runtime gate. A separate
Python verifier parses the profile without trusting CMake or a prior build tree,
requires the selected vendor directory to be an exact closed set of regular,
non-symlink files, recomputes six local digests, and compares the semantic
identity embedded in both `sqlite3.h` and `sqlite3.c`. Ten adversarial cases
prove that byte changes, undeclared material, an external symlink substitution,
a path escape, a hash-consistent semantic impostor, duplicate assignments, and
missing materials are rejected.

The first consolidated design still had a configuration/build cutpoint: CMake
hashed the vendor tree while generating the build graph, but an incremental
build could compile a retained file changed afterward without necessarily
re-running configuration. The same script-compatible native verifier now runs
as a phony dependency before the amalgamation target can build. A seven-case
native matrix includes an incoherent profile version plus an actual configure,
clean build, post-configure header mutation, and second build; the second build
fails before its probe target can compile.

The audit also found that release active-implementation projection v2 excluded
`cmake/`. The archive manifest still bound those files, but the release gate's
advertised active-source identity did not. Because the new dependency profile
and generated-header template are build authority, rev0905 advances that
projection to v3 and includes `cmake/` alongside source, tests, tools, fuzzers,
and retained dependencies. The package verifier requires v3 for rev0905 and all
later revisions; older v1/v2 package verification remains supported only for
their historical revision range.

## Heart of the mission

AnonSync is not primarily a file copier and not primarily a database wrapper.
Its mission is durable, bounded causal convergence in which authority is exact,
identity-bearing, crash-recoverable, and never fabricated by an observation,
summary, cache, pathname, transport session, or build report. Every layer that
can change which code interprets durable evidence is part of that authority
chain. Dependency selection and build configuration therefore belong inside the
same evidence discipline as database handles, filesystem descriptors, leases,
and manifests.

The practical rule for this revision is:

> One reviewed dependency identity must govern the bytes admitted at configure
> time, the declarations compiled into C++, the implementation linked into the
> process, the identity observed at runtime, and the source identity published
> by the release package.

## What was wrong

### 1. Configure/runtime provenance could split

Before rev0905, `CMakeLists.txt` hard-coded SHA-256 values for `sqlite3.c` and
`sqlite3.h`. `sync_sqlite_runtime.cpp` independently hard-coded
`SQLITE_VERSION_NUMBER` and `SQLITE_SOURCE_ID`. Updating one boundary without the
other was easy and review had to infer that two separate lists described one
artifact. The failure mode was not theoretical corruption of SHA-256; it was
ordinary maintenance drift that could make one trust gate stale or silently
weaker.

### 2. The retained dependency was only partially committed

The old configure gate did not hash `sqlite3ext.h`, the copied SQLite license,
or the upstream provenance record. It also did not compare the amalgamation to
SQLite's published SHA3-256. Those files ship in the source release and influence
API compatibility, legal/provenance review, or future dependency updates. A
partial inventory made it possible for the source tree to contain unreviewed
retained material while still printing “verified bundled SQLite.” Hashing a
known filename also followed symlinks, so a source-tree filename could have
selected matching bytes outside the retained vendor directory. Rev0905 closes
the inventory and rejects symlink, directory, and non-regular substitutions.

### 3. File hashes did not prove semantic agreement

A digest proves equality to the digest in the record, but it does not prove that
reviewers updated the record coherently. A profile could be edited to accept a
new header hash while leaving the version or source ID stale. The independent
verifier now extracts exactly one `SQLITE_VERSION`, `SQLITE_VERSION_NUMBER`, and
`SQLITE_SOURCE_ID` from both the header and amalgamation and requires both files
to match the profile exactly.

### 4. Build authority was outside the active-source projection

Projection v2 intentionally added `fuzz/` but still omitted `cmake/`. That was a
serious release-accounting blind spot once CMake modules became trust-bearing.
A package manifest mismatch would still be caught, but the release gate could
advertise the same “active implementation” digest after a CMake-profile change.
Projection v3 includes all CMake authority files and has a regression matrix
that proves a CMake mutation changes v3 while leaving legacy v2 behavior intact.

### 5. Attestation copied heap-backed strings on every policy check

The first implementation of the consolidated profile exposed eleven
`std::string` fields. Every call to `sync_sqlite_runtime_profile()` constructed
that object merely to obtain the immutable bundled flag and identity result,
causing repeated allocations and copies on database-open policy paths. Rev0905
uses process-lifetime `std::string_view` values into generated constants and a
`noexcept` attestation function. Compile-time tests pin that allocation-free API
shape.

### 6. Configure-time evidence could go stale before compilation

`file(SHA256 ...)` executes while CMake configures. It is not, by itself, a
content dependency that guarantees configuration runs again before every later
incremental compile. A retained amalgamation or header could therefore change
after a successful configure and be admitted by the ordinary build graph under
stale “verified” output. Rev0905 factors native verification into a
script-compatible CMake module and attaches an always-run dependency to the
bundled SQLite target. The target cannot build until current source-tree bytes,
inventory, entry types, and profile all re-attest.

## Implementation

### One reviewed profile

`cmake/AnonSyncBundledSqliteProfile.cmake` is the sole declarative dependency
record. It contains:

- semantic version and numeric version;
- release date and exact `SQLITE_SOURCE_ID`;
- official amalgamation archive name and published SHA3-256;
- the exact closed five-file retained inventory;
- local SHA-256 and official SHA3-256 for `sqlite3.c`;
- SHA-256 for `sqlite3.h`, `sqlite3ext.h`, `LICENSE.md`, and
  `UPSTREAM-PROVENANCE.md`.

The top-level CMake configure step first constrains the version to a canonical
dotted release and selects `third_party/sqlite-<version>` from that record. It
fails before generation if the inventory has duplicate or unsafe names, if the
directory contains any missing or undeclared entry, if an expected entry is a
directory or symlink, if a digest is malformed, or if any retained digest
differs. Every hash target must itself be a member of the closed inventory. The
generated header is private to `anonsync_sqlite_runtime`; it is not installed or
exposed as an ambient public include.

### Compile-time and live runtime binding

The runtime translation unit statically requires the bundled header's version,
version number, and source ID to equal the generated profile. At runtime it
compares `sqlite3_libversion_number()`, `sqlite3_libversion()`, and
`sqlite3_sourceid()` to those same constants. WAL activation still fails closed
unless header, linked runtime, corruption-fix classification, mutex profile,
compile options, and exact bundled provenance all agree.

The public evidence object reports the profile's reviewed archive, retained-file
inventory, file digests, and live identity result. System-SQLite builds retain
the prior semantics: they return `bundled=false` and empty bundled-review fields
while the normal header/runtime and WAL-fix gates continue to apply.

### Independent source-tree verification

`tools/verify_bundled_sqlite_profile.py` intentionally does not import CMake
output. It strictly accepts one assignment for every known key; checks coherent
version-number and archive naming; rejects missing, duplicate, empty, malformed,
unknown, or path-escaping profile fields; requires an exact flat inventory of
regular non-symlink files; hashes all retained materials; and reads semantic
macros from both core files. It produces compact or formatted JSON suitable for
release evidence.

`tools/test_verify_bundled_sqlite_profile.py` derives the selected version from
the profile rather than embedding `3.53.3`, so the test survives an isolated
vendor update. Its ten cases cover:

1. the clean source tree;
2. an appended byte in `sqlite3.c`;
3. a header whose hash was updated but whose semantic version is an impostor;
4. an altered extension header;
5. an undeclared extra vendor file;
6. an expected vendor filename replaced by a symlink outside the copied tree;
7. rewritten provenance;
8. a duplicate profile assignment;
9. a vendor-directory path escape in the profile;
10. a missing retained license.

### Native configure-and-build re-attestation

`cmake/AnonSyncVerifyBundledSqlite.cmake` contains the native closed-inventory,
schema-shape, and digest checks. The top-level configure invokes it directly.
`cmake/AnonSyncVerifyBundledSqliteAtBuild.cmake` invokes the same function in
script mode, and `anonsync_sqlite3_bundled_sqlite_profile_gate` is a phony
dependency of the amalgamation target. It therefore runs even when the target
otherwise appears up to date and does not rely on Python availability.

`tools/test_bundled_sqlite_native_build_gate.py` proves seven paths: clean native
verification, byte tamper, undeclared file, symlink substitution, profile path
escape, incoherent numeric version, and a post-configure mutation rejected by a
second build through the actual shared gate-attachment function.

### Active implementation projection v3

`tools/verify_release_package.py` now understands three projection generations:
legacy v1, v2 with fuzz sources, and v3 with fuzz plus CMake authority. The new
projection-policy test uses a synthetic inventory to prove inclusion/exclusion,
canonical digest construction, backward compatibility, and sensitivity to a
CMake-profile mutation. It also proves that rev0904 may retain v2 while rev0905
and later fail unless they declare v3. Rev0904's published v2 ZIP continues to
verify 31/31 with the rev0905 verifier.

## Validation

- Clean GCC 14 and Clang 17 Debug registries: **226/226** each.
- Focused GCC 14 ASan/UBSan runtime lane: **4/4**.
- Bundled profile clean verification: **10/10** checks.
- Bundled profile adversarial matrix: **10/10**.
- Native configure/build-gate adversarial matrix: **7/7**.
- Active projection version-policy matrix: **7/7**.
- Parent rev0904 ZIP backward verification: **31/31**.
- Final directory and ZIP verification are release-publication gates and are
  recorded externally because embedding a report into the bytes it attests
  would change those bytes.

## Explicit nonclaims

This is strong self-consistency and drift detection, not an external signature
or proof that an attacker able to rewrite the whole source tree cannot rewrite
the profile too. The release package remains self-attested by hashes inside the
same artifact. A higher-assurance distribution should add builder-generated,
externally verifiable provenance and signatures or transparency-log identity.

`SQLITE_SOURCE_ID` is useful semantic identity, not a substitute for hashing the
actual shipped amalgamation. SQLite documents that edited amalgamations may
alter the source-ID suffix, and historical SQLite release notes explicitly warn
that a forger can subvert source-ID edit detection. Rev0905 therefore requires
both exact bytes and exact runtime identity.

The bundled engine remains SQLite **3.53.3**. SQLite **3.53.4**, published on
2026-07-24, is newer and fixes issues in the 3.53.x line. This revision records
its official identities but does not claim to ship it. The dependency update
should stay isolated: replace the complete vendor bundle, update only the single
profile and provenance record, inspect upstream deltas, and rerun all VFS,
process-authority, crash, corruption, sanitizer, and package lanes.

## What remains missing

The strengthened dependency chain does not close AnonSync's largest product
holes. The highest-value work remains a bounded long-running supervisor and one
end-to-end causal loop that continuously admits filesystem observations,
exchanges manifests, streams resumable chunks, applies conflict policy and
durable effects, reconciles crashes, and exposes repair/quarantine state.
Retention/GC, indexes and hard resource budgets, cross-store coordination,
at-rest encryption and key rotation, and a formal anonymity/metadata/traffic
threat model remain incomplete.

There is also a build-integrity frontier beyond this revision. Future work should
bind compile definitions, toolchain identity, and dependency-fetch evidence into
externally signed provenance rather than merely reporting them. Reproducible
builds would make independent artifact comparison possible, but they do not by
themselves authorize a builder or source. The package verifier should continue
to treat build configuration as executable authority, not documentation.

## Primary-source research checked 2026-07-26

- SQLite 3.53.4 release and exact source identity:
  https://sqlite.org/releaselog/3_53_4.html
- SQLite current downloads and published archive hashes:
  https://sqlite.org/download.html
- SQLite compile-time source identity:
  https://www.sqlite.org/c3ref/c_source_id.html
- SQLite runtime version/source-ID APIs:
  https://sqlite.org/c3ref/libversion.html
- SQLite 3.21.0 source-ID edit-detection caveat:
  https://sqlite.org/releaselog/3_21_0.html
- CMake `configure_file(... @ONLY)` behavior:
  https://cmake.org/cmake/help/latest/command/configure_file.html
- CMake file hashing command:
  https://cmake.org/cmake/help/latest/command/file.html
- SLSA build provenance model and limits:
  https://slsa.dev/spec/v1.2/build-provenance
- SLSA build-integrity threats:
  https://slsa.dev/spec/v1.2/threats
