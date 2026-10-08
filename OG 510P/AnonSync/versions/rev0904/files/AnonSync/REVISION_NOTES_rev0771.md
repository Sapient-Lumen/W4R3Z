# AnonSync rev0771 — canonical checkpoint schema and snapshot authority

## Heart of this revision

A checkpoint is durable evidence. It is safe to consume only when its exact finite schema, declared schema-version row, peer-ingress cohost commitment, and all data reads belong to one verified SQLite view. A successful `CREATE ... IF NOT EXISTS`, a matching schema cookie, or a statement that merely prepares cannot supply that authority.

## Correctness and refactor work

- Extracted checkpoint DDL and migration layout knowledge from the roughly 24,000-line domain implementation into one canonical finite schema catalog.
- Preserved historical layouts instead of flattening compatibility: v3 remains its reviewed 19-object shape, while v4 carries the later lineage objects.
- Made checkpoint creation prove its postcondition. Pre-existing same-named objects are no longer silently accepted merely because `IF NOT EXISTS` returned successfully.
- Strengthened peer-ingress cohost attestation to bind the exact checkpoint schema-version row and the complete reviewed object manifest. Resetting SQLite's schema cookie therefore cannot conceal semantic drift.
- Precomputed the reviewed layouts once and bounded catalog object count, per-row SQL, aggregate SQL, and version metadata before canonicalization.
- Established schema isolation before the first metadata lookup, including legacy v1/v2 readers whose formerly unqualified names could be redirected by hostile TEMP objects.
- Put creation recheck, resume projection, and operator projection inside scope-bound read snapshots, closing the gap where attestation could describe state A while later rows came from state B.
- Replaced the old weak test cohost (metadata plus an arbitrary probe object) with the real finite manifest and retained adversarial drift, shadowing, version, and bound cases.

## Audit conclusion

The severe failure mode was not one malformed SQL string. It was **competing schema authorities**: embedded production DDL, a weaker peer-ingress model, historical version assumptions, and fixtures that could each bless a different container. The correction is structural: one reviewed catalog is consumed by creation, migration, attestation, and tests; read isolation begins before lookup and lasts through consumption.

The secondary repository audit is in `REVISION_EVIDENCE/rev0771/REPOSITORY_HYGIENE.md`. Current packaging excludes generated builds, compiler products, nested ZIPs, VCS metadata, and external symlinks instead of copying validation waste into the active cube.

## Measured delta and validation

- Source delta against rev0770: +0 / -0 across 0 files.
- Debug CTest: None tests, None failures.
- Release CTest: None tests, None failures.
- ASan/UBSan is recorded as an optional independent gate; raw statuses and logs are retained without rewriting failures.

## Next correctness seam

The next boundary is transaction-order authority across SQLite and durable payload bytes: temporary write, file fsync, atomic rename, directory fsync, database transition, receipt publication, and acknowledgement need one documented order plus crash injection at every edge. The schema work ensures evidence is interpreted by the right model; the next revision should ensure that model never points to bytes that were not durably committed.
