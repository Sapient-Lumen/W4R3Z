# AnonSync rev0798 — exact SQLite geometry and trailing-byte authority

Prepared from the last byte-verifiable parent available in this cloudtainer,
`AnonSync-rev0796-2026.07.15.09.39-sealedbytes-walexclusion-vfspin-stagedrehash-lineagetruth.zip`
(SHA-256 `f883596f190b76a1e23cb35f187e799322b6d55886070d5d55ca1592361baeeb`).
A rev0797 archive was not available to this execution environment, so rev0798
does not fabricate a parent digest or claim unverified lineage through it.

## Heart of the mission

AnonSync is an **evidence-authorized convergence engine**. Observation is not
authority. A pathname, descriptor, file size, SQLite header field, successful
open, query result, or backup completion becomes authority only after the owner
of the relevant invariant proves the exact relationship needed for promotion.

For a sealed sidecar-free SQLite snapshot, the authenticated file extent and
the page extent SQLite interprets must be identical. Otherwise a manifest can
truthfully authenticate bytes that SQLite ignores and a restore never
reproduces.

## Severe defect corrected: authenticated suffix bytes were not logical state

Rev0796 sealed and hashed the whole source descriptor, but it did not prove that
all sealed bytes belonged to the SQLite database page graph. SQLite accepts a
database with a complete extra page appended after the header-declared page
count. Queries still see the canonical rows and `PRAGMA page_count` still
reports the original count. `sqlite3_backup` copies the logical page graph and
discards that authenticated suffix.

The permanent rev0798 exploit proof demonstrates all three facts:

1. ordinary SQLite accepts the padded input and returns the original row;
2. SQLite backup emits the shorter canonical database, losing the suffix;
3. AnonSync rejects the padded source before allocating a private staging
   directory.

This matters even when the suffix is inert. Without exact geometry, the system
can claim that signed bytes were restored when only a normalized subset was.
That is lineage laundering.

## Refactor: one pure geometry authority owner

`src/persistence/sqlite_snapshot_geometry.*` is an independently linked C++20
boundary. It promotes a 100-byte SQLite header plus an exact descriptor byte
count only after proving:

- the complete 16-byte `SQLite format 3\0` magic;
- a valid 512..65536 power-of-two page size, including SQLite's `1 => 65536`
  encoding;
- equality of the file-change counter and version-valid-for field, which is
  SQLite's condition for treating the in-header database size as current;
- a nonzero page count within a reviewed 262,144-page hard ceiling;
- exact equality of `page_count * page_size` and descriptor bytes;
- caller policy can tighten, but cannot widen, either the one-GiB byte ceiling
  or the page ceiling.

The pure proof is four fresh Ninja actions and two first-party translation
units (369 lines). It does not link OpenSSL, SQLite, path security, or the core
monolith.

## Seal integration

`SealedSqliteSnapshot` now verifies geometry before creating its 0700 staging
directory. The destination descriptor is opened read/write solely so the copied
header can be re-read without reopening a pathname. Geometry is then re-proved
on:

1. the retained source descriptor before staging;
2. the writable private-copy descriptor after fsync and mode transition;
3. the retained readonly descriptor after reopening through the guarded path;
4. every later `verify_unchanged_or_throw` seal assertion.

The move-only seal retains page size, page count, exact bytes, and the tightening
policy as process-local evidence. Existing byte digest, inode, timestamp,
sidecar, parent-directory, and VFS identity checks remain in force.

## Second-order corrections

The rev0796 constructor allowed a caller to set `maximum_bytes` above the stated
one-GiB maximum. Rev0798 makes both byte and page ceilings monotone: caller input
may revoke authority but cannot mint more.

The new leak proof initially used a global `/tmp` staging-directory inventory.
Parallel CTest could mistake another legitimate seal test's live directory for
a leak. The three staging-sensitive tests now share a resource lock, preserving
parallel test execution without weakening the assertion.

## Coverage-guided proof

`fuzz/fuzz_sqlite_snapshot_geometry.cpp` implements the real
`LLVMFuzzerTestOneInput` interface. It explores arbitrary and synthesized-valid
headers, exact/trailing/truncated extents, stale counters, both page-size
encodings, zero/tight/widened policies, and success invariants. Clang 17
libFuzzer/UBSan completed 100,000 executions without a finding.

## Validation

- Parent rev0796 package verification: **25/25**.
- GCC 14 Debug/`-Werror`: full build and **59/59 CTest**.
- Pure geometry proof: **35 checks x 20/20**.
- Integrated seal proof: **68 checks x 20/20**.
- Trailing-byte/backup exploit proof: **13 checks x 20/20**.
- GCC 14 ASan/UBSan focused lane: **5/5 repetitions** for all three proofs.
- Clang 17 strict conversion/sign-conversion/shadow `-Werror`: **5/5**.
- GCC 14 `-O3 -DNDEBUG` first-party lane: **5/5**.
- Clang 17 libFuzzer/UBSan: **100,000 executions**.
- Geometry architecture audit: **20/20**; existing seal audit: **37/37**.

The optimized bundled SQLite C amalgamation emitted one GCC
`-Wstringop-overread` diagnostic during its separate C compilation. The
first-party C++ targets were compiled with `-Werror` and passed; no claim is made
that the third-party amalgamation was warning-clean under that optimizer build.

## What remains missing

Exact file geometry bounds and binds bytes/pages; it does not bound total SQLite
verification CPU, VDBE steps, decoded rows, retained text bytes, allocator/RSS,
temporary storage, or blocked I/O. The next resource boundary should be a
lifetime-owned verification guard and then a disposable worker process with OS
resource limits and a small result protocol.

The highest-value system proof remains a crash-cut VFS/protocol oracle that
interrupts writes and publication at every durable boundary, restarts in a new
process, and independently checks both SQLite structural integrity and permitted
AnonSync outcomes.

Authentication, exact persistence, and convergence machinery still do not by
themselves establish anonymity, payload confidentiality, metadata privacy,
forward secrecy, or post-compromise recovery. Those claims require an explicit
adversary and key-lifecycle contract.

## Primary research references

- SQLite database file format and header validity fields:
  <https://www.sqlite.org/fileformat.html>
- SQLite online backup API:
  <https://www.sqlite.org/backup.html>
- SQLite testing and crash/fault simulation strategy:
  <https://www.sqlite.org/testing.html>
