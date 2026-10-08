# AnonSync rev0979

## Durable retention mark and policy

- Added the fixed-width, checksum-framed
  `.anonsync-payload-retention-mark-v1` record.
- Bound each mark to the exact immutable store identity digest and eleven-field
  private single-link identity-inode observation.
- Persisted exact source operation, inactive-evidence, explicit-pin, visible,
  payload, transient-namespace, candidate-set, and durable-witness digests.
- Persisted the SQLite source generation so digest-level unpin/repin ABA
  within one retained database lineage cannot inherit an older grace interval.
- Kept that generation explicitly non-authoritative across replica-database
  rollback or replacement: an exact older image can recreate the generation and
  source digests, so future collection must bind a recovery epoch or reset age.
- Added bounded grace, candidate count/bytes, and future collection count/bytes
  policy frontiers with strict overflow and store-capacity validation.
- Moved the exact store-capacity check ahead of writer-fence acquisition and
  complete payload enumeration. A held-identity-lock regression proves both
  impossible count and byte frontiers fail without publishing a mark or
  changing payload/transient namespace state.
- Kept the record explicitly deletion-free: no reclaim, quota, quarantine,
  rename, or unlink authority is serialized.

## Exact publication handoff

- Published through the same exact writer-fenced payload snapshot that computed
  the complete candidate witness.
- Avoided an immediate second complete payload-root observation.
- Atomically created or exact-metadata-replaced the record and reopened the
  committed bytes before returning.
- Preserved crash truth: a committed record can survive a final typed source-
  drift failure, but its older forward-lineage source generation remains stale
  until a current mark replaces it.
- Preserved primary exception provenance when best-effort post-failure record
  observation itself cannot open, parse, allocate, or complete rooted reproof.
- Excluded the fixed internal mark from payload and transient accounting and
  their canonical digests so metadata publication cannot self-invalidate its
  own witness.

## Adjacent audit/refactor

- Added `retention_mark_observation_known()` so synchronized damaged evidence is
  distinguishable from byte-cold `ReadOnlyInspect` output.
- Made malformed, torn, wrong-size, and stale-identity records visible but
  unusable and conditionally replaceable only beneath the exact writer fence.
- Recorded the fail-closed downgrade boundary: rev0978 complete scans reject the
  new internal basename rather than misinterpreting it.
- Removed a divergent unsealed retention-intent branch and reconstructed the
  accepted change from exact sealed rev0978 bytes.
- Corrected an overbroad claim that publication never rehashes: it avoids an
  added scan, while the existing complete observation still hashes whenever
  exact verification evidence is unavailable.
- Recorded that mark replacement generation is only usable-predecessor
  continuity evidence and restarts at one after absence or damage.
- Added release-source structural checks for the codec, store handoff,
  same-lineage ABA fence, rollback boundary, policy boundary, runtime tests,
  audit, notes, and package policy.

## Validation

Exact rev0979 C++ source passed a clean GCC 14.2 Debug graph (532/532 configured build edges), 258/258 preseal registered runtime tests, and an independent 40/40 GCC product replay in 114.17 seconds. The finalized registered structural authority audit passed 362/362 checks, accounting for all 259/259 registered tests across the unchanged C++ bytes and final release prose. Focused exact-source suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 30 retention-mark, 640 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 463 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 158 local-control, 87/87 observer, and 6/6 observer-race checks. A clean Clang 17 Debug product dependency graph completed 243/243 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 40/40 product tests passed serially in 155.48 seconds with leak detection and halt-on-error. Focused sanitizer proof passed the 640-check payload-store suite in 11.33 seconds at 514,824 KiB peak RSS, the 463-check folder-owner suite in 37.23 seconds at 1,467,772 KiB peak RSS, and the 158-check local-control suite in 0.68 seconds at 113,860 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0978 parent SHA-256 matched 5d8c9bc1470f3c7bcd38ed039dc69d766bc1ff9fdddba1ee4ef9de49a045d734 and passed 41/41 wrapper-aware package checks. Validation excluded source-divergent retention prototypes, shared-cache and in-tree build contamination, self-restarting mutable-source launchers, interrupted rev0979-named sanitizer processes, and every result not bound to the byte-reconciled clean source. The binary-aware source patch reconstructed all 13/13 changed active files and the complete 573-file projection byte-for-byte and by mode. The final active implementation projection contains 573 files / 26,681,569 bytes with SHA-256 7ef1c72b253f25a8e8fb1154aafbc4ce0220891b4de7eebef6ce139eb76e7f7b.
