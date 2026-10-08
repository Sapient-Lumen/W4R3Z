# Revision notes — rev0963

The bounded quarantine inventory is restart-discoverable through ordinary service startup.
## Mission move

Rev0963 makes the complete bounded diagnostic quarantine discoverable through
ordinary owner status. Rev0961 preserved exact corrupt-byte evidence and
rev0962 released an exact digest pair, but status exposed only the last action.
After restart or multiple incidents, an older retained pair could consume
capacity without a supported way to rediscover the selector required by
`quarantine-release`.

## C++ implementation

- Added `SyncReplicaFilePayloadStoreQuarantineInventoryStatus` and exact entry
  records containing expected digest, observed digest, and observed size.
- Added a fixed-width, allocation-free process projection for all sixteen
  possible retained images.
- Complete writable payload scans prepare that projection and publish it only
  after their existing final verification, fault, root, and lease cutpoints.
- Exact preserve/release namespace observation now produces the same canonical
  projection.
- Mutations prepare a successor before rename/unlink, forget stale status before
  mutation, and publish the successor only after final pathname, durability,
  lease, and rooted-authority reproof.
- Non-mutating exact absence republishes the complete observation.
- Added an exact-owner-thread, filesystem-cold
  `quarantine_inventory_status()` accessor. It performs no scan, lease, open, or
  hash.
- Reused one monotonic age helper for scrub and quarantine observation ages.
- Advanced canonical live and terminal service status to
  `anonsync.peer-service.status.v10`.
- Bound service readiness to the live allocation-free inventory-known witness,
  not only the historical initial-repair bit. Four counters expose the exact
  initial snapshot handoff, entry count, duplicate observation count, and any
  mutation full scan.

## Audit/refactor

The folder-wake restart oracle no longer equates one current catalog path with
one retained payload object. Its create-then-edit sequence correctly retains two
immutable payloads while exposing one current path, and now proves that the
initial service handoff carries both without another payload-store observation.

An unfinished draft added `quarantine-list` to the local socket and performed a
new complete traversal per query. Rev0963 removes that duplicate command and
query-time authority path. Existing complete observers already pay the required
namespace work; status now retains only their bounded result. Derived private
basenames are not cached because exact digest pairs already reconstruct them.

The audit also found that the empty-folder initial-repair fast path could mark a
service ready while its fresh payload-store owner still had an unknown retained
set. Rather than weaken restart discoverability, rev0963 takes one complete
initial snapshot, moves it into the existing convergence pass, and asserts that
convergence performs no second complete payload observation. The live ready
predicate rechecks the current cache so a failed preserve/release mutation that
revokes presentation truth cannot hide behind the historical repair bit. The
structural audit binds that handoff, the filesystem-cold status and readiness
accessors, exact mutation successors, rejected query-time list ownership, and
shipping route/process oracles as one authority boundary.

A complete-registry run also falsified an older I2P test assumption: closing a
SAM control TCP connection before writing a marker on a separate data
connection does not order what the peer kernel observes. The regression now
half-closes the control stream and waits for Linux `TCP_INFO` to report
`TCP_FIN_WAIT2` before releasing the data marker. Stale-session recovery is thus
proved by an acknowledged FIN rather than scheduler luck.

## Runtime proof

The focused payload-store test covers process-cold unknown status, known empty
publication, restart rediscovery of two entries in canonical order, exclusion
from authoritative inventory, exact release successor publication without a
second scan, non-mutating exact absence, and second-restart rediscovery.

The real configured-service process test validates the v10 shape, a known empty
inventory after initial convergence, exact one-entry inventory after same-inode
preservation, exact empty inventory after release, unchanged authoritative
bytes/inode/recheck state, same-PID readiness, and terminal retention of the
empty successor. The folder-wake process test proves the startup contract for
an otherwise empty folder and again after restart: readiness follows exactly
one complete payload snapshot handoff, convergence performs zero duplicate
snapshot observations, status polling performs no traversal, and later file
work preserves the known-empty diagnostic set.

## Product boundary

This is discoverable diagnostic evidence, not user-restorable version history.
There is no persisted creation age, user path, causal version, retention class,
TTL, reachability pin, automatic collection, archive browser, restore command,
or authenticity claim based on the quarantine filename.

See `RESTART_DISCOVERABLE_QUARANTINE_INVENTORY_AUDIT_rev0963.md`.

## Validation

The exact final source completed a fresh GCC 14.2 Debug 527/527-edge graph
and exact-source no-work re-attestation. The complete 258/258 registry passed
in bounded serial shards, and the independent 39/39 product lane passed.
Focused suites passed 84 resumable-SHA, 19 scrub-state, 26 verification-index,
576 payload-store, 30/30 rooted-POSIX, 92 network-model plus 41 generated-
operation, 296 SQLite-owner, 360 folder-owner, 110 sync-once, 2,043 TLS, 17
integrity-evidence, and 92 local-status-socket checks. The structural audit
passed 197/197 checks.

Clang 17 ASan/UBSan completed a fresh 238/238-edge product dependency graph and
exact-source no-work re-attestation. All 39/39 product tests passed in bounded
serial shards with leak detection and undefined-behavior halt-on-error. No
retained compiler, linker, sanitizer, runtime-error, or leak diagnostic remains.

The exact rev0962 parent SHA-256 matched and passed 41/41 wrapper-aware checks.
The binary-aware source patch reconstructs 14/14 changed active files exactly.
The active implementation projection binds 567 files / 25,657,014 bytes at
SHA-256 5d066b7a91ac61fff7aa61016f03434af9c1ef9a988e513b0fa84d69b908df07.
Final publication remains conditional on the release gate, exact manifest,
wrapper directory and ZIP verifiers, CRC and canonical path/no-symlink policy,
and clean-extraction equality for every path, byte, entry type, and permission
mode.

## Nonclaims

The inventory is the last complete leased process observation. A raw standalone
store owner may remain unknown until eligible work, but the retained service
makes one such observation a readiness prerequisite. Unknown is not itself an
integrity fault; it prevents a ready claim until a complete owner cutpoint
republishes truth. The view is not continuously live, a durable index, a hostile-
same-UID defense, a portable network-filesystem guarantee, or power-loss
qualification. The first measured Resilio uninstall workflow and ordinary user
version/restore owner remain open.
