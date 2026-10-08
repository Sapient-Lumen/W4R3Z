# rev0881 primary-source research and inference

Research was checked online on 2026-07-22 against primary operating-system,
POSIX, and SQLite documentation.

## Filesystem and live-context sources

- Linux namespace handles: https://man7.org/linux/man-pages/man7/namespaces.7.html
  Opening `/proc/pid/ns/*` yields a handle that keeps the namespace alive;
  matching namespace files expose matching device/inode identity. This supports
  a retained live mount-namespace capability, not a reboot-stable identity or a
  defense against a privileged process/kernel adversary.
- Linux boot ID: https://docs.kernel.org/admin-guide/sysctl/kernel.html
  `/proc/sys/kernel/random/boot_id` identifies the current boot and remains
  stable during that boot. It is an epoch observation, not an authentication
  secret or a permanent root identity.
- `statvfs(3)`: https://man7.org/linux/man-pages/man3/statvfs.3.html
  `f_namemax` reports the maximum filename length for the observed filesystem;
  unspecified/zero observations cannot safely mint a guessed ceiling.
- `pathconf(3)`: https://man7.org/linux/man-pages/man3/pathconf.3.html and POSIX
  `fpathconf()`: https://pubs.opengroup.org/onlinepubs/009696799/functions/fpathconf.html
  `_PC_NAME_MAX` is descriptor-relative and may be indeterminate without error.
  It supports a conservative local preflight, not canonical identity or an
  immutable tree-wide law.
- POSIX `open()`: https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html
  The actual descriptor-relative syscall remains the final authority for whether
  a name can be materialized in the live directory and namespace.

## Dispatch and transaction sources

- SQLite transactions: https://sqlite.org/lang_transaction.html
  SQLite permits one simultaneous write transaction; `BEGIN IMMEDIATE` starts
  the write transaction immediately and can fail with `SQLITE_BUSY` when another
  writer exists.
- SQLite isolation: https://sqlite.org/isolation.html
  Separate connections are isolated and writes are serialized. This supports a
  bounded local guard that excludes competing database writers while a row and
  cutpoint are re-attested. It does not create an atomic transaction with a
  socket, filesystem, or remote database.
- Linux `send(2)`: https://man7.org/linux/man-pages/man2/send.2.html
  A successful or failed local send call does not imply end-to-end delivery; the
  API can also block or report local queue conditions. Therefore frame
  construction, first-byte dispatch, remote durable acceptance, visible effect,
  and terminal receipt remain distinct authority frontiers.

## Applied inference

Canonical operation/path validation must remain replica-stable. Receiver-local
materialization policy should be an explicit pre-effect result observed from a
retained capability. Uncertain support should defer to the descriptor-relative
syscall rather than reject shared history or guess.

An in-memory claim copy is historical evidence that a claim once existed, not
live dispatch authority after arbitrary callback code. Re-reading under
`BEGIN IMMEDIATE`, sampling owner-controlled time only after exact identity,
and retaining the transaction through bounded no-callback construction creates
a defensible *local* cutpoint. Keeping that writer capability across network I/O
would instead create unbounded lock duration and still would not make the remote
side atomic.

Boot UUID and namespace inode/mount observations constrain live authority but
must not become permanent cross-restart equality requirements without an
explicit, rollback-protected rebind ceremony.

## Speculation and next work

The next narrow correction should move from local frame construction to
transport-owned first-byte authority. Two plausible designs deserve experiments:

1. a transport primitive that receives an exact claim identity and performs a
   final owner re-attestation immediately before writing the frame header; or
2. durable frame ownership, where encoded bytes/digest, claim identity, channel
   binding, attempt state, and settlement frontier are persisted and recovered
   as one explicit state machine.

The first is smaller but still has a crash boundary between local send and
sender settlement. The second can make ambiguity explicit but increases durable
state, payload retention, key/channel epoch questions, and compaction burden.
Neither should hold a SQLite write transaction across arbitrary blocking I/O.

Separately, unavailable boot identity should become typed observation data that
the outbox owner can quarantine durably. Repair of already staged
unmaterializable paths needs an operator/device-authorized transition; silently
deleting or rewriting them would manufacture history. A future indexed owner
should be differentially tested against the existing O(history) correctness
oracle rather than replacing it by assertion.
