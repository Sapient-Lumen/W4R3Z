# AnonSync rev0799

AnonSync is an **evidence-authorized convergence engine**. A successful syscall,
query, signature check, database open, pointer lookup, or commit is an
observation. It becomes authority only after the boundary that owns the
invariant verifies the exact bytes, identity, process, generation, lifetime,
policy, relationship, schema, resource budget, and durability evidence needed
for the transition.

## Current revision: finite hostile-snapshot interpretation

Rev0798 proved that a sealed SQLite file has exact page geometry. Exact bytes do
not, however, make interpretation finite. A geometrically valid snapshot could
still spend unbounded SQLite VM work and cause the verifier to retain multiple
attacker-sized hash containers. The pending-effect report also verified one
autocommit snapshot and projected rows from a later snapshot, so a concurrent
writer could separate the reported rows from the heads and counts that were
verified.

Rev0799 introduces an independently linked, lifetime-owned SQLite verification
budget. It installs the connection's progress handler before hostile SQL is
prepared or stepped, derives tighter authority from the sealed byte/page
geometry, and enforces reviewed ceilings for VM callbacks, callback interval,
rows, decoded text, retained text, and elapsed time. Callback denial is sticky,
value-free, and surfaced as a typed resource exception after SQLite returns
`SQLITE_INTERRUPT`.

The read-only replay-ledger verifier now fuses cross-table state into one ordered
map instead of several attacker-sized hash sets and maps. The pending-effect
report performs verification and projection in one explicit read transaction
under one resource budget. An executable concurrency proof commits a mutation
between those phases and confirms that the report remains bound to its verified
historic snapshot.

## Validation

- GCC 14 Debug/`-Werror`: full build and **61/61 CTest**.
- Focused resource proof: **63 checks x 20/20**.
- Geometry/staging binding proof: **13 checks x 20/20**.
- Production read-only verifier: **11 checks x 10/10**.
- GCC 14 ASan/UBSan focused lane: **5/5** for both focused proofs.
- Clang 17 strict conversion/sign-conversion/shadow `-Werror`: **5/5**.
- GCC 14 `-O3 -DNDEBUG -Werror`: **5/5**.
- Resource architecture audit: **45/45**; existing seal and geometry audits:
  **37/37** and **20/20**.
- Parent rev0798 package: **25/25** verifier checks.

Full evidence is under `REVISION_EVIDENCE/rev0799/`.

## Deliberate limits

The in-process budget bounds selected work and retained-text dimensions, not
SQLite's complete heap, allocator metadata, page cache, blocked kernel I/O,
JSON serialization after database close, or the consequences of a SQLite or
kernel defect. Text is accounted after exact extraction, so one field can still
allocate up to the separately configured SQLite scalar limit before denial.
Hostile snapshot interpretation should ultimately run in a disposable worker
with OS CPU, memory, file, syscall, and wall-clock limits.

The project still lacks a crash-cut VFS/protocol oracle, an executable formal
merge algebra, and an explicit anonymity/confidentiality/key-lifecycle threat
model. Authentication, exact persistence, and convergence machinery do not by
themselves establish those privacy properties.

## Build

```bash
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DANONSYNC_USE_BUNDLED_SQLITE=ON \
  -DCMAKE_CXX_FLAGS=-Werror
cmake --build build --parallel 4
ctest --test-dir build --output-on-failure --parallel 4
```

Focused boundary:

```bash
cmake --build build --target anonsync_sqlite_verification_budget_test
ctest --test-dir build --output-on-failure \
  -R 'sqlite_(verification_budget|snapshot_geometry_binding)'
```
