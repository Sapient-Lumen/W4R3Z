# AnonSync rev0771 — checkpoint schema authority and snapshot audit

## Mission boundary

The checkpoint is durable evidence, not a convenient cache. A reader may resume or report from it only when the exact historical layout, version row, cohost container commitment, and subsequent data reads all belong to one isolated SQLite view. Neither `CREATE ... IF NOT EXISTS`, SQLite's schema cookie, nor a successful prepare is sufficient authority by itself.

This revision centralizes the finite checkpoint schema catalog, removes duplicated DDL/migration authority from the domain monolith, binds cohost attestation to the exact version row and full manifest, bounds hostile catalog work, establishes TEMP isolation before the first metadata lookup (including legacy v1/v2 readers), and holds creation recheck/resume/operator reads inside scope-bound snapshots.

## Measured source delta

- Added lines: **0**
- Removed lines: **0**
- Changed files: **0**

- No source delta detected.

## Audit conclusions

1. **Single authority is the key refactor.** The finite reviewed schema layouts should be compiled once and consumed by creation, upgrade, and attestation. A second hand-maintained manifest inevitably drifts and can accidentally bless a weaker fixture or legacy shape.
2. **The schema cookie is not commit truth.** It can detect likely catalog movement, but exact normalized object SQL plus the expected version row and container commitment carry semantic authority.
3. **Isolation must precede lookup.** Establishing `main`/TEMP policy after reading `checkpoint_metadata` leaves legacy readers vulnerable to name redirection. The boundary belongs before the first statement preparation.
4. **Attestation and data reads need one snapshot.** Otherwise a valid manifest can be checked at state A and payload/receipt rows consumed from state B.
5. **Fail-closed work must also be bounded.** Object count, row SQL length, aggregate SQL, and metadata length limits prevent a hostile cohost from turning verification into memory or CPU amplification.
6. **Creation needs postcondition proof.** `IF NOT EXISTS` is acceptable only as an idempotent mechanism followed immediately, in the same protected boundary, by exact finite-layout verification.

## Static findings requiring continued review

- **high — writable-schema-use** at `src/sync_peer_ingress_schema.cpp:438`: writable_schema can bypass ordinary catalog invariants; production use requires a narrowly documented migration boundary.
- **review — possibly-unqualified-catalog-reference** at `src/sync_peer_ingress_lifecycle.cpp:3423`: Review whether this reference is schema-qualified before hostile TEMP objects can influence resolution.
- **review — possibly-unqualified-catalog-reference** at `src/sync_peer_ingress_payload_store.cpp:176`: Review whether this reference is schema-qualified before hostile TEMP objects can influence resolution.
- **review — possibly-unqualified-catalog-reference** at `src/sync_peer_ingress_payload_store.cpp:178`: Review whether this reference is schema-qualified before hostile TEMP objects can influence resolution.
- **review — possibly-unqualified-catalog-reference** at `src/sync_peer_ingress_payload_store.cpp:182`: Review whether this reference is schema-qualified before hostile TEMP objects can influence resolution.
- **review — possibly-unqualified-catalog-reference** at `src/sync_peer_ingress_schema.cpp:456`: Review whether this reference is schema-qualified before hostile TEMP objects can influence resolution.
- **review — possibly-unqualified-catalog-reference** at `src/sync_peer_ingress_schema.cpp:456`: Review whether this reference is schema-qualified before hostile TEMP objects can influence resolution.

## Largest remaining source units

- `third_party/sqlite-3.53.3/sqlite3.c` — 269,614 lines
- `src/sync_domain.cpp` — 24,524 lines
- `third_party/sqlite-3.53.3/sqlite3.h` — 14,350 lines
- `src/reporting_selftests.cpp` — 4,499 lines
- `src/sqlite_replay_ledger.cpp` — 4,341 lines
- `src/sync_peer_ingress_lifecycle.cpp` — 3,778 lines
- `include/anonsync_core.hpp` — 3,500 lines
- `src/runner.cpp` — 2,199 lines
- `src/sync_peer_ingestion.cpp` — 1,945 lines
- `src/sync_operator_cli.cpp` — 1,253 lines
- `src/sync_peer_ingress_wire.cpp` — 983 lines
- `tests/peer_ingress_schema_attestation_test.cpp` — 776 lines

The largest-unit list is not a mandate for mechanical splitting. Future decomposition should follow invariant ownership: schema catalog, repository/snapshot, peer-ingress container attestation, transition state machine, and operator projection.

## Adversarial test-evidence index

Keyword occurrence counts in test sources: temp=38, shadow=7, manifest=32, schema_version=9, schema cookie=0, snapshot=31, mutation=35, drift=4, cohost=15, v1=35, v2=38, v3=14, v4=2, oversized=1, bound=38, hostile=13. Exact file/line/snippet mappings are in `audit.json`; keyword counts are navigation aids, not coverage claims.

## Validation

- **debug-fresh**: configure=126, build=126, ctest=126; parsed tests=None, failures=None
- **release**: configure=126, build=126, ctest=126; parsed tests=None, failures=None
- **asan-ubsan**: configure=126, build=126, ctest=126; parsed tests=None, failures=None

Raw configure/build/CTest logs and original exit codes are retained beside this report. Sanitizer support is recorded as an optional gate because platform/toolchain runtime behavior can differ; Debug and Release are required.

## Primary-source research

- [Transactions](https://www.sqlite.org/lang_transaction.html): A read transaction presents one historical snapshot; starting it before metadata attestation keeps subsequent reads in the same database view.
- [Isolation In SQLite](https://www.sqlite.org/isolation.html): Separate connections can observe different committed states; an explicit read transaction closes the attestation-to-read race.
- [The Schema Table](https://www.sqlite.org/schematab.html): sqlite_schema is ordinary queryable catalog state and must be schema-qualified when TEMP shadowing is in scope.
- [PRAGMA trusted_schema](https://www.sqlite.org/pragma.html#pragma_trusted_schema): Turning trusted_schema off is defense in depth against application-defined functions or virtual tables embedded in schema expressions.
- [PRAGMA schema_version](https://www.sqlite.org/pragma.html#pragma_schema_version): The schema cookie is a change signal, not a cryptographic or semantic commitment to exact DDL.
- [sqlite3_set_authorizer](https://www.sqlite.org/c3ref/set_authorizer.html): An authorizer constrains operations during preparation but does not replace exact schema/data attestation.

## Next correctness seam

Move from catalog authority to **transaction-order authority**: specify and test the ordering among SQLite commit, payload/file fsync, directory fsync, receipt publication, and acknowledgement. The state machine should expose one typed durable transition record so crash injection can compare every operation boundary against an executable oracle. Schema correctness prevents false interpretation of evidence; transaction ordering prevents correctly interpreted evidence from referring to bytes that were never durably committed.
