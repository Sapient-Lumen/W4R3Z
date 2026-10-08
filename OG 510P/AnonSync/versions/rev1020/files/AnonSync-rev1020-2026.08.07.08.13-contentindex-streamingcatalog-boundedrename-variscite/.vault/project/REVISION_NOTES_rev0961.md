# Revision notes — rev0961

## Mission move

Rev0961 turns rev0960's exact payload-integrity alarm into one bounded operator recovery action. The owner no longer has to edit AnonSync's private content store
by hand:

```text
anonsync_sync quarantine --socket ABSOLUTE_SOCKET \
    --expected LOWERCASE_SHA256 --observed LOWERCASE_SHA256
```

The command accepts one exact active corruption pair, preserves that wrong byte
image outside payload authority with a same-inode no-replace rename, and leaves
the existing authenticated convergence owner to fetch and prove correct content.
The operation is explicit, bounded, and fail closed. It is not automatic
quarantine, version history, restore, retention, or garbage collection.

## C++ implementation

- Added canonical quarantine names binding both the expected immutable digest
  and exact observed corrupt digest.
- Added `SyncReplicaFilePayloadStore::quarantine_corrupt_payload_or_throw()`.
- Requires an exact process-local active integrity witness before mutation.
- Obtains the existing exclusive lease on the exact reader-fenced identity
  inode and re-proves root, identity, namespace, capacity, and pathname state.
- Rehashes current source bytes before any move and returns typed stale, changed,
  repaired, absent, idempotent, or successful dispositions.
- Uses the existing rooted Linux no-replace rename helper, directory `fsync`,
  source-absence proof, destination pathname proof, and same-device/inode proof.
- Synchronizes the exact open corrupt source bytes before making the renamed
  diagnostic pathname durable; existing exact destinations are also
  synchronized after their complete-byte reproof.
- Rehashes an already retained exact destination before success; if the same
  corrupt authoritative name has reappeared, it also rehashes and removes that
  duplicate source so repeated identical corruption cannot remain permanently
  idempotent-but-blocked. A canonical filename alone is never evidence.
- Excludes canonical quarantines from payload inventory and targeted access,
  while complete scans still validate their private regular-file shape and
  enforce a fixed sixteen-entry frontier whose aggregate bytes cannot exceed
  the active indexed-byte budget.
- Returns typed `entry_capacity_exceeded` or `byte_capacity_exceeded` outcomes
  when an otherwise valid new preservation request reaches that frontier. This
  is an expected non-mutating operator result, not a daemon-terminating
  exception. A pre-existing structurally over-budget namespace remains a
  fail-closed scan error.
- Rejects pre-existing quarantines during fresh-store bootstrap, including
  the standalone payload-adoption path, rather than assigning unbound
  diagnostic evidence to a newly published store identity.
- Revokes process verification/checkpoint/scrub acceleration after a successful
  namespace mutation while retaining the fail-closed integrity obligation until
  a complete scan proves absence or good bytes.
- Leaves `quarantine_basename` empty for non-mutating outcomes. Status reports a
  retained name only after the exact destination exists and its bytes were
  re-proved.

## Local control and lifecycle refactor

- Added the exact request
  `quarantine EXPECTED64 OBSERVED64\n` and strict response schema
  `anonsync.local-quarantine.response.v1`.
- Extended, rather than forked,
  `SyncLocalStatusSocketActionSnapshot`: drain, recheck, and at most one exact
  quarantine request are observed under one mutex.
- Repeated requests for the same pair advance and coalesce; a different pair is
  rejected while pending.
- Owner completion cannot erase a newer same-pair generation, future/regressed
  completions reject, and post-drain requests do not advance state.
- One action condition, one exact combined wait baseline, and one shutdown seal
  preserve accepted pre-seal work in terminal accounting.
- The socket worker remains capability-free with respect to payload bytes,
  folders, SQLite, TLS, routes, and scheduling effects.

## Service and status

- Added owner-thread quarantine request observation, priority, bounded lease
  deferral, typed completion, and exact-pair transition handling.
- Quarantine is attempted before operator recheck and automatic integrity
  recovery because it is the pending namespace mutation.
- Successful preservation does not clear the alarm. Correct bytes must be
  re-admitted and ordinary convergence must complete first.
- Status advances to `anonsync.peer-service.status.v8`.
- Live and terminal JSON share canonical quarantine status/result renderers.
- New counters distinguish requests observed/coalesced, attempts, completions,
  byte images preserved, and observed-content changes.
- The operation truthfully reports one mutation-authority full scan needed to
  re-admit the now-missing expected digest; it does not reuse rev0960's
  duplicate-scan-free handoff claim across a namespace mutation.

## Tests and audit

- Payload-store tests cover stale/wrong pairs, changed corruption, already
  repaired content, absent content, successful same-inode preservation,
  byte-reproved idempotence, canonical parser rejection, bootstrap rejection,
  capacity bounds, typed nonfatal entry/byte capacity completion, retained
  active-fault authority, and read-only-owner rejection.
- Local-control tests cover exact bytes, generation/coalescing semantics,
  different-pair exclusion, owner completion races, drain/shutdown ordering,
  combined waits, PID binding, and malformed responses.
- The real configured-service process oracle proves same-PID lease deferral,
  exact fault transitions, shipping CLI acceptance, same-inode retained bytes,
  authoritative re-admission with a distinct inode, forced recheck recovery,
  retained history, truthful scan accounting, clean drain, and socket removal.
- The adjacent audit found and corrected a misleading result field: stale and
  non-mutating outcomes no longer expose a destination name that was never
  retained. It also corrected normal frontier exhaustion from a process-killing
  exception into a typed completion and added source-file synchronization
  before the diagnostic rename.
- See
  `EXACT_CORRUPT_PAYLOAD_QUARANTINE_AND_LINEARIZED_LOCAL_ACTION_AUDIT_rev0961.md`.

## Validation

The exact frozen source completed a fresh GCC 14.2 Debug 527/527-edge graph
and exact-source no-work re-attestation. The complete 258/258 registry passed
serially in 115.95 seconds, and the independent 39/39 product lane passed in
60.36 seconds. Focused suites passed 84 resumable-SHA, 19 scrub-state, 26 verification-index,
551 payload-store, 30/30 rooted-POSIX, 92 network-model plus 41 generated-
operation, 296 SQLite-owner, 360 folder-owner, 110 sync-once, 2043 TLS, 17
integrity-evidence, and 83 local-status-socket checks. The structural audit
passed 180/180 authority checks.

Clang 17 ASan/UBSan completed a fresh 238/238-edge product dependency graph and
exact-source no-work re-attestation. All 39/39 product tests passed serially with
leak detection in 123.14 seconds. The core payload-store target then passed all
551 focused checks under the same sanitizer profile in 8.93 seconds. No retained
compiler, linker, sanitizer, runtime-error, or leak diagnostic remains.

The exact rev0960 parent SHA-256 matched and passed 41/41 wrapper-aware checks.
The binary-aware source patch reconstructed 15/15 changed active files exactly.
The active implementation projection binds 567 files / 25546979 bytes at
SHA-256 b83dd20d24e0814451a7ebea063e8759905292c9fd9915b569d422971eaa002f.
Final publication remains conditional on the release gate, exact manifest,
wrapper directory and ZIP verifiers, CRC and canonical path/no-symlink policy,
and a clean extraction preserving every path, byte, entry type, and permission
mode.

## Nonclaims

- The sixteen-entry quarantine frontier is diagnostic evidence, not a complete
  retention or quota policy.
- There is no restore command, archive browser, retention age, reachability pin,
  automatic eviction, or crash-safe garbage collection.
- Requests and generations are process-local and do not survive service exit.
- No automatic quarantine occurs; exact operator intent is mandatory.
- The same-effective-user threat boundary remains cooperative, not hostile.
- Linux no-replace rename, `flock`, and pathname-socket behavior are not yet a
  portable cross-platform or network-filesystem contract.
- Power-loss behavior still requires filesystem/storage-stack qualification.
- Rename identity, directories, portable metadata, conflict UX, selective sync,
  changed-block transfer, many-share ownership, live public Tor/I2P privacy
  qualification, and a measured first Resilio uninstall workflow remain open.
