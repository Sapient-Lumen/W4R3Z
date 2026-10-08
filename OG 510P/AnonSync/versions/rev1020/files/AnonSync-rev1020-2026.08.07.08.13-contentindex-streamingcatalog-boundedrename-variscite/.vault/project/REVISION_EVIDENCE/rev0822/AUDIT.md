# Rev0822 audit

## Boundary selected

Rev0821 left `backup_snapshot()` as the remaining ordinary path that could delete and directly own an entire destination SQLite family. The governing invariant is:

> A live ledger handle authorizes capture of one consistent source image. Verified resident bytes authorize publication of exactly those bytes. Neither capability authorizes deletion or writable SQLite interpretation of an unrelated destination namespace, and row-count equality does not establish ledger identity.

## Severe parent defects reproduced

Rev0821 called `unlink_sqlite_family(snapshot_path)` before backup, created the destination directory, opened the final destination as a writable SQLite database, copied directly into it, ran canonicalization there, closed it, reopened its pathname for verification, and compared only loaded entry count.

The same 415-line C++ test is compiled unchanged against parent and current. It substitutes a different valid-looking 64-hex `ledger_instance_id` without changing decision rows. Rev0821 exits 2 because backup succeeds and publishes the substituted identity. Rev0822 rejects the resident image before creating the requested missing destination directory and passes all 36 checks.

## Production correction

Backup now performs a non-mutating destination-family preflight, rejecting WAL, SHM, and journal evidence without deleting it. It captures the already-open full-mutex source connection through SQLite's online backup API into a private `:memory:` database on the pinned VFS. `trusted_schema=OFF` and `temp_store=MEMORY` are read back exactly; private `VACUUM` canonicalizes the image to standalone 1/1 form. Exact page geometry is checked before private open and after copy. The final `sqlite3_serialize()` allocation is adopted directly under a matching `sqlite3_free` deleter rather than copied through `std::vector`.

The same resident bytes feed the read-only logical verifier and the atomic publisher. Publication is authorized only when durable entry count, durable decision head, `ledger_instance_id`, transition line count/head, and outbox state match the live backend. The complete gate exposed one overreach during development: a session-local successful-transition counter resets after reopen and cannot be compared to durable transition rows. That telemetry comparison was removed and a structural audit now forbids its return.

Only after source verification does backup acquire a directory-creating path-family guard. Exact resident bytes publish through the typed atomic owner, then destination sidecar absence is reasserted. Typed publication outcome and residue evidence survive the bool facade.

## Test and release-surface refactor

The 36-check namespace test proves prior main-file replacement, foreign atomic-publisher temp preservation, canonical 1/1 output, reusable live source, durable identity-substitution rejection before directory creation, and fail-closed preservation of all three portable SQLite sidecar classes.

A new 25-check source audit prevents destination staging/open/deletion, count-only authorization, session-local telemetry authorization, early directory creation, missing source-budget ordering, and non-binary publication from returning. Existing process, seal, geometry, restore, atomic-publication, and verification-budget audits were updated where representation or dependency ownership changed. The release verifier requires both the executable proof and structural audit.

## Validation

- exact rev0821 parent: ZIP 25/25, directory 21/21;
- same-source differential: parent exit 2; current 36/36;
- Debug all-target build passed; final dependency closure reported no work;
- all 101 registered tests passed in one uninterrupted 32.76-second CTest run;
- seven structural audits: 276/276;
- focused repeat: 75/75 executions and 3,450/3,450 reported checks;
- GCC 14 and Clang 17 `-Werror`: all four changed C++ translation units;
- scoped Clang 17 ASan/UBSan: seal, backup integration, and reopened-ledger effect transition all pass; leak detection and bundled-SQLite instrumentation excluded;
- nondefault 8192-byte page live capture passed; and
- source patch replay reproduced all 12 changed active files byte-for-byte.

## Broader audit and explicit limits

`unlink_sqlite_family()` now has one production caller: `load(reset=true)`. That ordinary flag still mints destructive family authority and is the next highest-priority correction.

The live-copy byte/page policy rejects an already-oversized source before opening private destination state and rejects an oversized copied image afterward. It does not yet prove that a concurrently growing source cannot transiently allocate beyond policy during `sqlite3_backup_step(-1)`. A destination page ceiling or bounded-step protocol with adversarial growth tests should follow.

Sidecar checks remain point-in-time and cooperative locks do not isolate a hostile same-UID directory writer. Hostile SQLite parsing remains in the long-lived process. Windows, arbitrary power-loss, full-project sanitizer, leak sanitizer, distributed convergence, confidentiality, anonymity, metadata hiding, key lifecycle, and secure erasure are not claimed.
