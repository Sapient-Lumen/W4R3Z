# AnonSync rev0978

## Process-store live-capability composition

- Replaced the exact-owner-only live-capability registry with a bounded brokered
  process-store scope keyed by rooted attestation, identity basename, and
  immutable expected store identity.
- Made independently opened same-process owners contribute snapshots, opened
  payloads, targeted accessors, and mutation batches to one canonical cutpoint.
- Added a fresh non-durable process-store incarnation after the final owner and
  every issued capability release the scope and a later owner recreates it.
- Kept exact snapshot handoff bound to the issuing owner's verification cache,
  integrity epoch, rooted authority, folder identity, limits, and registration.
- Preserved fail-closed record, scope, registration-ID, and activity-generation
  frontiers.

## Writer-fenced retention observation

- Built and sorted the immutable causal-root projection before taking the
  writer fence, then added a private complete payload snapshot that retains the
  exact store-global exclusive identity lease through physical merge, bounded
  candidate probes, final SQLite comparison, and final root/identity reproof.
- Excluded new cooperating payload namespace observation and mutation during the
  retention interval.
- Added page-bounded descriptor-rooted exact-inode payload-use probes for every
  returned unreferenced candidate.
- Added typed `not_applicable`, `exclusive_available_at_cutpoint`, and
  `busy_at_cutpoint` entry dispositions.
- Added a page-specific digest over the source, cursor, limit, entries,
  classifications, and exact-inode probe results.
- Moved allocation-heavy causal grouping and canonical sorting before the
  exclusive lease so ordinary synchronization is stalled only for physical
  observation, merge, bounded inode probes, and final cutpoints.
- Added `writer_fenced_candidate_page_entry_count`, preserving the complete
  already-probed logical page when the independent status-byte frontier emits
  only a canonical entry prefix.
- Advanced the deletion-free mark to v4.

## Restart-stable candidate identity

- Added a page-invariant `durable_candidate_witness_digest` that binds the exact
  causal, evidence, pin, visible, payload, transient-namespace, and complete
  candidate-set cutpoints while excluding process-local incarnation/activity.
- Deliberately did not persist a mark, apply retention policy, quarantine a
  collection candidate, reclaim bytes, or unlink payloads.

## Adjacent audit/refactor

- Split same-process independent-owner truth from cross-process nonclaims in the
  operator JSON contract.
- Advanced live and terminal status to `anonsync.peer-service.status.v23` and the
  local retention response to `anonsync.local-retention-plan.response.v5`.
- Strengthened the real configured-service oracle to parse all new fence,
  witness, count, and payload-use fields.
- Linked the local response regression to the canonical JSON parser so new
  response assertions do not depend only on substring matching.
- Reconciled the structural audit with the actual process-store broker,
  exact-owner handoff boundary, writer-fence lifetime, and candidate probe.
- Removed an unsealed standalone retention-mark codec, library, and test target
  that had no shipping persistence owner, policy consumer, recovery path, or
  collection operation; the product graph remains on the existing planner.
- Recorded the advisory-lock and open-file-description limits from Linux and
  POSIX primary documentation rather than promoting the probe to mandatory-lock
  or cross-process capability-census authority.

## Validation

Exact rev0978 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests in bounded final-source shards, and an independent 39/39 product replay in 86.36 seconds. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 630 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 450 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 158 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 349/349 checks. An isolated Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer. All 39/39 product tests passed in bounded lanes with leak detection and halt-on-error: the allocation-heavy 450-check folder-owner test passed separately in 30.71 seconds at 1,454,776 KiB peak RSS, and the remaining 38/38 product tests passed in 114.43 seconds. Focused sanitizer proof also passed the 630-check payload-store suite in 9.06 seconds at 503,672 KiB peak RSS and the 158-check local-control suite in 0.74 seconds at 112,900 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0977 parent SHA-256 matched acf4f08be987f2fb5d44b2ff1a0e4b34a460248ac29f72ff0f3498f7d7f0e73f and passed 41/41 checks under the rev0978 wrapper-aware verifier. The binary-aware source patch reconstructed all 15/15 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,575,951 bytes with SHA-256 f47ed3037fb6a2e553a2b278e7dd591f3b97afd4d62e44e8d0fb0dcb69962c89. Validation excluded superseded monolithic sanitizer invocations, interrupted full-registry wrappers, competing orphan release launchers, stale or source-divergent runs, and a transient Python bytecode cache removed before projection sealing.
