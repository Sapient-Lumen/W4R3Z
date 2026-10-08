# Revision notes: AnonSync rev0860

## Mission increment

A planner-selected subset is already a narrow authority candidate. Loading an
entire persisted manifest to validate that subset broadens work and failure
surface without broadening legitimate authority. Rev0860 replaces that pattern
in resume-transfer claim and execution with an exact-generation, main-schema,
point-probe owner whose row and byte limits are explicit.

## Principal corrections

1. Removed both complete source-chunk vector reconstructions from the transfer
   claim and executor.
2. Added `SyncSqliteManifestChunkSubsetVerifier` and a 34-check adversarial
   corpus.
3. Qualified durable chunk, apply-intent, and entry evidence with `main` so a
   TEMP shadow cannot redirect proof.
4. Added a literal two-row duplicate sentinel and exact SQLite storage-class
   decoding.
5. Added complete caller preflight, including SQLite signed-integer
   representability for both chunk offsets and lengths.
6. Bound selected row, metadata, and payload work to planner summaries and the
   frozen persisted manifest cardinality.
7. Bounded adjacent persisted text copies and made the new boundary mandatory
   in packages from rev0860 onward.
8. Added a 63-check structural audit that rejects reintroduction of the former
   amplification path.

## Compatibility

No protocol, manifest-identity, digest, planner, or workorder spelling changes.
Only invalid, ambiguous, stale, redirected, duplicate, or over-budget evidence
is newly rejected.

## Validation summary

GCC Debug all-target closure; 160/160 registered tests in nine exact ranges;
48/48 registered audits; 34/34 focused owner checks; 63/63 new audit checks;
Clang 17 `-Werror` full-core build and 2/2 selected tests; focused GCC ASan+UBSan
34/34 with 25 repeated executions; exact replay of the seven-file active delta
across all 307 active files; sealed-parent verification 26/26 ZIP and 22/22
directory.
