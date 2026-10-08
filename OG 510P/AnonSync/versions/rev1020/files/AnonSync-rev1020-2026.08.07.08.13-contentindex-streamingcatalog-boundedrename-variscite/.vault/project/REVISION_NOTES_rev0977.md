# AnonSync rev0977

## Exact same-owner live payload-capability cutpoint

Rev0977 extends the deletion-free retention mark across live payload-store
capabilities owned by the exact retained C++ store owner.

- Added a bounded process-local registry for live snapshots, opened payload
  descriptors, targeted accessors, and mutation batches.
- Added one same-owner incarnation digest and exact monotonic registration IDs;
  same-count capability replacement no longer aliases.
- Added a separate non-durable activity generation that advances on every
  successful register and unregister; complete create-and-destroy activity
  between equal set observations no longer aliases.
- Replaced a wrapping `fetch_add` incarnation sequence with fail-sticky
  saturating compare-exchange allocation.
- Made move-only registration the first capability-state member so payload
  descriptors and authority state are released before the root disappears.
- Strengthened exact snapshot-origin proof with the shared live-capability
  registry in addition to the verification cache and durable root identity.
- Excluded only the planner's own exact live snapshot from the observed set.
- Conservatively roots all physical payloads for live snapshots/targeted access
  and roots exact digest/size objects for opened descriptors.
- Bracketed retention projection with equal opening/final capability cutpoints;
  set drift or interval activity fails at typed stage
  `retention_live_capability_set`.
- Deliberately kept the activity generation out of the canonical set digest,
  serialized response, and deletion-free mark so quiescent pages remain
  canonical while the process-local bracket still detects ABA activity.
- Advanced the deletion-free mark to domain v3, service status to
  `anonsync.peer-service.status.v22`, and the local retention response to
  `anonsync.local-retention-plan.response.v4`.
- Added per-entry same-owner live-root evidence plus exact counts, bytes, owner
  identity, set digest, and unreferenced-root aggregates.
- Added runtime regressions for all-payload snapshot roots, same-count snapshot
  replacement, complete create-and-destroy interval ABA, exact opened-descriptor
  roots, and root release.
- Restored historical README and structural-audit schema claims from sealed
  rev0976 after an unsealed global replacement had rewritten them incorrectly.
- Kept the private targeted-access boundary private. A narrowly declared
  test-only friend bridge observes the private cutpoint without adding a
  shipping method or response field.

Rev0977 remains deletion-free. It does not bind independently opened store
owners, other processes, already copied outbound buffers, every active pass or
receiver lifetime, retention policy, durable mark intent, collection
quarantine, restart revalidation, or unlink. See
`EXACT_LIVE_PAYLOAD_CAPABILITY_CUTPOINT_AUDIT_rev0977.md`.

## Payload-use lease and current snapshot reader fence

Rev0977 closes the opened-descriptor removal seam left by the exact rev0976
retention cutpoint without adding collection authority.

- Added the stable cross-process protocol
  `anonsync:sync-replica-file-payload-use-flock-lease:v1`.
- Re-entered the current shared payload-store identity fence for every byte
  reopen from a retained complete snapshot.
- Added a shared exact-inode payload-use lease to snapshot selection, targeted
  one-digest selection, and bounded range copying.
- Moved that shared lease with
  `SyncReplicaFilePayloadStoreOpenedPayload`, while deliberately releasing the
  global store lease before large local publication or network I/O.
- Required exact corruption quarantine rename and diagnostic-quarantine release
  unlink to acquire the candidate inode exclusively under the existing global
  exclusive store lease.
- Established one fixed lock order: global store identity first, exact payload
  inode second; no path upgrades or reverses those locks.
- Added current-reader-fence, same-process inode contention, final-close release,
  namespace nonmutation, and fork-inherited cross-process descriptor
  regressions.
- Corrected stale folder-owner comments that still described snapshot reuse as
  safe only because the store was append-only.
- Removed an accidental literal NUL from the edited C++ regression and extended
  the structural audit to reject embedded NUL bytes in required release source
  and records.

Rev0977 remains deletion-free. The exact retention response still denies
opened-sender root completeness because no writer-fenced collection operation
consumes this protocol yet. Active-pass, receiver, publication, mutation,
policy, durable mark, collection quarantine, restart reobservation, and final
unlink authority remain incomplete. Advisory locks do not protect against
noncooperating same-UID or privileged writers, and remote-filesystem behavior
still requires qualification. See
`PAYLOAD_USE_LEASE_AND_SNAPSHOT_READER_FENCE_AUDIT_rev0977.md`.

## Combined authority boundary

The two mechanisms are complementary. The registry makes exact same-owner
process capabilities visible to the deletion-free mark; the cooperative inode
lease prevents an already-issued descriptor from racing a future namespace
removal. Neither mechanism roots independently opened owners, payload names not
yet opened, copied transport buffers, or noncooperating writers. Rev0977 adds
no retention policy, durable mark, collector, reclaim decision, or unlink path.

## Validation

Exact rev0977 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests in a final serial replay (129.22 seconds), and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 613 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 448 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 339/339 checks. An isolated Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed serially in 144.09 seconds with leak detection and halt-on-error. Focused sanitizer proof passed the 613-check payload-store suite in 13.33 seconds at 484,272 KiB peak RSS, the 448-check folder-owner suite in 39.78 seconds at 1,453,628 KiB peak RSS, and the 155-check local-control suite in 1.44 seconds at 105,116 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0976 parent SHA-256 matched 44d90e8b74fffe16239ea0e6b1516a215950d7bc1d558344e7c64b5189a7f566 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 18/18 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,498,367 bytes with SHA-256 d4ad87ef909365a2af2515451da83248a94680bce23f0056dfff0f3c8db0b8b6. Validation excluded overlapping or stale shared-tree launchers, interrupted wrappers, divergent unsealed branches, and every result not bound to the exact final active projection.
