# Revision notes — rev0960

## Mission move

Rev0960 adds an explicit owner-operated current-byte payload recheck to the one
shipping C++ linked-peer service. It closes a practical recovery gap: the
background rotating scrub is intentionally bounded and eventual, but an owner
who suspects storage damage needs a way to force proof now without stopping the
service, deleting databases, or waiting for the scrub cursor to arrive.

```text
anonsync_sync recheck --socket ABSOLUTE_SOCKET
```

The command returns a strict PID-bound JSON acceptance or rejection. Acceptance
advances a process-local request generation; it is not completion. The existing
status command reports requested, started, and completed generations, pending
state, retry delay, exact hash work from the last completion, snapshot handoff,
duplicate-scan counters, and whether completion also recovered an integrity
fault.

## C++ implementation

- Added the exact local request `recheck\n` to the owner-only mode-0600 Unix
  status/control socket.
- Added monotonic bounded request generations and strict response schema
  `anonsync.local-recheck.response.v1` with connected-peer PID validation.
- Serialized drain and recheck through one mutex and exposed one
  `SyncLocalStatusSocketActionSnapshot` to the owner thread.
- Removed the separate stop and generation getters and the redundant atomics so
  callers cannot recreate a split-read or mixed-synchronization shutdown race.
- Added `seal_actions_for_owner_shutdown()`. Before terminal status is frozen for
  signals, local drain, cycle limits, or runtime limits, the owner latches drain
  and captures the final accepted generation under the same mutex. Requests after
  that cutpoint reject without advancing the generation.
- Bound retry wakeup to the same action mutex/condition predicate, rejecting a
  future generation baseline and preventing notify-before-wait loss.
- Rejects recheck serialized after drain without incrementing the generation;
  accepted pre-drain generations remain visible in terminal accounting.
- Added owner-thread generation observation, pending/coalesced accounting, and
  bounded retry semantics. A first newly pending request may bypass an old
  automatic retry cutpoint; later requests cannot clear backoff established by
  an actual attempt.
- Added `snapshot_rechecking_current_bytes_or_throw()`, which uses the complete
  rooted payload-store scanner with both process and durable verification reuse
  disabled.
- Asserts at the returned snapshot boundary that reused entries/bytes are zero
  and hashed entries/bytes equal the exact indexed totals.
- Moves the exact resulting snapshot into ordinary folder convergence rather
  than paying for a second complete payload-store observation.
- Consolidated automatic integrity recovery and operator recheck in one shared
  completion cutpoint for convergence, native-I2P freshness, fault history,
  readiness restoration, scheduling, and duplicate-scan accounting.
- Added `OperatorPayloadRecheckCompleted` and status schema
  `anonsync.peer-service.status.v7`.
- Centralized live and terminal `payload_recheck` JSON in one canonical renderer,
  removing duplicated field ownership.

## Failure and recovery behavior

A cooperative writer lease conflict does not terminate the daemon or discard the
request. The same process keeps the authenticated listener and owner-only socket,
reports typed lease deferral, and retries at the bounded service cutpoint.
Multiple requests coalesce without producing a hot `flock` loop.

A digest mismatch enters the existing fail-closed payload-integrity state. The
accepted generation remains pending, readiness is false, exact expected and
observed digests remain visible, and ordinary authority is withheld. After
external repair, the explicit recheck again forces current bytes and only then
hands the snapshot through ordinary convergence. Successful completion restores
readiness in the same PID and retains immutable recovery history.

## Adjacent audit and refactor

The recovered implementation originally had separate action getters, redundant
atomics beneath a mutex, and two hand-maintained payload-recheck JSON blocks.
Rev0960 removes those drift surfaces: one mutex-linearized action state is the
sole owner observation, one explicit owner seal closes admission before terminal
rendering, and one renderer serves both live and terminal status. The common
real-process terminal parser now rejects duplicate JSON object keys rather than
accepting implementation-dependent evidence.

The release-policy audit also removed a duplicated rev0960 mandatory-file block
from `verify_release_package.py` and now requires exactly one revision branch.
The duplicate happened to be masked by set semantics, but retaining it would
create two textual authorities and invite later drift.

The audit also corrected the corruption process oracle so it does not assume
`readdir` returns digest basenames in lexical order. Either corrupt object may be
reported first; repairing only that object must leave the other mismatch
observable.

The lexical structural audit follows shared helper ownership after the refactor
instead of requiring all authority logic to remain in thin public wrappers. It
still explicitly disclaims semantic proof; fresh compiler, runtime, sanitizer,
and package evidence remain load-bearing.

See `OWNER_TRIGGERED_PAYLOAD_RECHECK_AUDIT_rev0960.md`.

## Preserved boundaries

- The payload store's complete descriptor-rooted scanner remains namespace,
  capacity, and byte authority.
- The request generation is process-local scheduler/presentation state and never
  content authority.
- Exact snapshot handoff requires the same retained store owner, verification
  cache, thread, root, attestation, folder identity, limits, and integrity epoch.
- The ordinary convergence algorithm remains the only shipping catalog/local/
  remote/replica settlement path.
- Direct TCP, Tor, and I2P remain routes to the same authenticated semantics.
- `ReadOnlyInspect` stays mutation-free and cannot invoke forced recheck.

## Nonclaims

Rev0960 does not claim that acceptance means completion, durable recheck requests
across daemon exit, subpath selection, live progress or cancellation,
filesystem-wide forced reads, quarantine, automatic restore, version retention,
reachability pinning, garbage collection, hostile same-UID protection, portable
Unix-socket security, network-filesystem lock equivalence, universal power-loss
behavior, rename/directory/metadata completion, many-share supervision,
selective synchronization, live public Tor/I2P qualification, or completion of a
named measured Resilio uninstall workflow.

## Validation

GCC 14.2.0 Debug completed a fresh 527/527-edge graph and exact-source
no-work re-attestation. The complete 258/258 registry passed serially in
134.10 seconds; the independent 39/39 product lane passed in 54.26 seconds.
Focused suites passed 84 resumable-SHA, 19 scrub-state, 26 verification-index,
519 payload-store, 30/30 rooted-POSIX, 92 network-model plus 41 generated-
operation, 296 SQLite-owner, 360 folder-owner, 110 sync-once, 2043 TLS, 17
integrity-evidence, and 69 local-status-socket checks.

Clang 17 ASan/UBSan completed a fresh 238/238-edge product graph and
exact-source no-work re-attestation. All 39/39 product tests passed serially
with leak detection in 124.68 seconds, with no retained compiler, linker,
sanitizer, runtime-error, or leak diagnostic.

The structural authority audit passed 166/166 checks. The exact rev0959 parent
SHA-256 matched and passed 41/41 wrapper-aware ZIP checks. The binary-aware
rev0960 patch reconstructed 16/16 changed active files byte-for-byte and by
mode. The active implementation projection binds 567 files / 25,420,532 bytes
at SHA-256 61fed36a59412827b9aec3e5d6604c37fecf5107de647cadef28422bf4086788.

The release remains publishable only when `RELEASE_GATE.json`, the exact active
projection, and `MANIFEST.sha256` bind the final hidden project; the wrapper
directory and ZIP verifiers pass; ZIP CRC/path/no-symlink policy passes; and a
clean extraction preserves every path, byte, entry type, and permission mode.
