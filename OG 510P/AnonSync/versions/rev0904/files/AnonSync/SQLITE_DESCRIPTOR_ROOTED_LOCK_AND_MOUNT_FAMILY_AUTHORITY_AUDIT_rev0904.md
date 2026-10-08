# SQLite descriptor-rooted lock and mount-family authority audit — rev0904

## Executive finding

AnonSync's heart is not copying bytes. It is preserving **bounded, exact,
identity-bearing evidence** long enough that independent replicas can derive the
same authorized state after crashes, retries, concurrency, and partial failure.
The local product spine is therefore credible only when observation cannot
silently become authority and when a path checked at one frontier cannot name a
different object at the next.

Rev0904 advances that mission by carrying the selected SQLite deployment
directory into a private VFS registration and binding the main database,
rollback journal, WAL, and shared-memory family to that retained directory.
During the audit, however, two defects were found in the initial descriptor-
rooted implementation:

1. the VFS retained an extra descriptor for the SQLite main inode; and
2. namespace-inode and `st_dev` checks did not distinguish a bind-mounted family
   member introduced inside the already-authorized mount namespace.

The first defect was severe. Traditional POSIX record locks are associated with
a process, but closing **any** descriptor that the process holds for the same
file can release all of that process's locks for that file. An auxiliary
"evidence descriptor" could therefore invalidate SQLite's lock proof when it
was closed, even though SQLite's own handle remained live. Rev0904 removes that
lifetime pattern. Pre-open inspection for one product authority uses a short-
lived handle delegated to the same bundled Unix VFS before that authority has a
live file. SQLite's process-wide Unix-driver bookkeeping can therefore defer the
close when another same-inode SQLite connection owns locks. Once the authority's
connection exists, reads, synchronization, and exact-handle attestation operate
through its already-open main `sqlite3_file` while holding the connection mutex.

The second defect was an authority gap. A file bind mount can replace a WAL or
other family pathname without changing the process mount-namespace inode, and
it can preserve the same `st_dev`. Rev0904 freezes the parent mount identity
reported by Linux `statx` and requires every existing family member to report
that exact mount identity before VFS delegation. The check is allocation-free
and opens no same-inode descriptor, so it does not recreate the lock defect it
was designed beside.

## Mission model

AnonSync currently treats exact accepted history as authority and derived
summaries as acceleration. Applied to a local SQLite store, that means all of
the following must remain distinct:

- the deployment manifest selects an intended logical database path;
- a retained directory descriptor selects a live parent directory object;
- the private VFS controls SQLite's operational file family;
- the opened SQLite connection proves it came through that exact VFS instance;
- the opened main `sqlite3_file` proves the connection still occupies the
  retained family name;
- store-internal deployment binding proves the database belongs to the selected
  deployment and role;
- durability reconciliation proves which exact image reached an accepted crash
  cutpoint.

No one item substitutes for the others. A digest cannot prevent pathname
replacement. A retained parent descriptor cannot prove a sidecar stayed on the
same mount. A live SQLite handle cannot prove that it was opened through the
reviewed VFS. A manifest cannot legitimize a foreign but structurally valid
store. Rev0904 keeps these proofs compositional rather than collapsing them into
one ambiguous "path is safe" boolean.

## Cumulative descriptor-rooted VFS implementation

The unreleased rev0902/rev0903 checkpoints introduced the private VFS now
completed by rev0904. The release contains the cumulative implementation from
rev0901 onward.

### Registration and lifetime

`SqlitePathFamilyGuard` preflights the exact selected main path and sidecar
family. `register_sqlite_descriptor_rooted_vfs_or_throw` then:

1. duplicates and identity-checks the retained parent directory descriptor;
2. records the process incarnation and mount-namespace authority;
3. probes and freezes the Linux directory-resolution capability;
4. captures the parent's `statx` mount identity;
5. proves the existing main is a regular single-link object with the approved
   device/inode identity and retained mount identity;
6. registers a private, uniquely named VFS whose delegated paths are rooted at
   `/proc/self/fd/<retained-parent-fd>/`;
7. keeps that registration alive until every wrapped SQLite file is closed.

The product authority object is ordered so that the SQLite connection closes
before the private VFS unregisters and before the retained parent authority is
released.

### File-family mediation

The wrapper recognizes only the reviewed main, rollback-journal, WAL, and SHM
names. It rejects anonymous temporary-file opens, named `DELETEONCLOSE`, lock-
proxy redirection, null-I/O closure, and unreviewed file-control path mutation.
Every delegated open must retain a single-link regular-file identity at the
reviewed family name. Close-time cleanup is revalidated so a late hostile SHM
replacement cannot turn SQLite cleanup into deletion of a foreign name.

Mount-namespace authority is checked at pathname-resolution frontiers instead
of every page I/O or lock callback. The hot path retains the already-open file
object; pathful operations reprove the process context, retained parent
descriptor, procfs descriptor bridge, and frozen mount identity.

### Exact connection and handle proof

A product connection is accepted only when:

- `sqlite3_db_filename(..., "main")` equals the authorized logical path;
- `SQLITE_FCNTL_VFS_POINTER` returns this exact private VFS object;
- `SQLITE_FCNTL_FILE_POINTER` returns a live wrapped main-file object;
- the wrapper belongs to this registration state and exposes the expected
  wrapper method table;
- its retained delegated path is the exact procfs descriptor-rooted path; and
- the underlying opened file still occupies the retained family name.

The check is performed under SQLite's connection mutex. A same-path connection
opened through another VFS cannot satisfy it.

## Severe lock-lifetime correction

### Why the auxiliary descriptor was wrong

The first descriptor-rooted implementation retained an independent writable
file descriptor for the main database. It was intended to make bounded reads
and `fsync` independent of ambient pathname resolution. That intention was
reasonable but the lock model was not.

SQLite's Unix VFS normally uses traditional `fcntl` record locks. On Linux and
POSIX systems with that model, locks are process-associated and are released
when the process closes any descriptor referring to the file. Therefore:

- SQLite could hold a RESERVED lock through its own descriptor;
- AnonSync could close the independent evidence descriptor; and
- the kernel could release SQLite's process locks while the connection still
  appeared live and authoritative.

Retaining the auxiliary descriptor until after connection close reduced some
exposures but did not make the abstraction safe. Exception paths, registration
teardown, future refactors, and multiple same-process connections could still
close a same-inode descriptor at the wrong time. The correct invariant is
stronger: **do not create an independent same-inode descriptor while live
SQLite record locks are part of the authority proof.**

### Replacement design

Rev0904 splits the evidence operations by lifecycle:

- `read_bounded_main_file_before_open_or_throw` is valid only while that private
  VFS has no live files. It delegates a read-only open to the same bundled Unix
  VFS, validates the exact retained name, performs a bounded read, verifies
  stable identity, and closes before this authority opens its product
  connection. Delegation is essential: the Unix driver can defer the close if a
  different connection in the process currently holds same-inode locks.
- `read_bounded_main_file_or_throw(sqlite3*, ...)` accepts the live serialized
  product handle, proves the exact VFS and wrapped main file, and reads through
  that existing `sqlite3_file`.
- `sync_main_file_and_parent_directory_or_throw(sqlite3*, ...)` synchronizes the
  already-open main file through its `xSync`, then synchronizes the retained
  parent directory. It does not reopen the main inode.

The product `ProductSqliteDatabaseAuthority` obtains a serialized database
borrow and passes the exact handle to these operations. Bootstrap candidate
header preflight uses the pre-open form. Rollback-image durability promotion
pins a SQLite read transaction, then performs both reads and synchronization
through the live handle.

### Adversarial proof

The process-authority test acquires a real SQLite RESERVED lock and asks a fork
child to observe contention. It verifies contention before auxiliary pre-open
inspection, after the delegated pre-open read, and after auxiliary VFS teardown.
Only rollback/connection close may release the lock. This is a kernel-observed
regression, not a source-text assertion.

## Same-namespace mount-family correction

### Why namespace identity and `st_dev` were insufficient

A process can remain in the same mount namespace while a privileged or
user-namespace-capable actor adds a bind mount at a family pathname. The mount
namespace's device/inode identity does not change when its contents change.
Further, a bind mount can present an object from the same filesystem, preserving
`st_dev`. A check that asks only "am I in the same namespace?" or "is this the
same device?" can therefore accept a different mount object.

### Allocation-free relative mount observer

`sync_posix_observe_relative_mount_noexcept` is a shared leaf primitive. Given a
retained directory descriptor, one relative path component, a frozen
resolution capability, and a retained mount identity, it classifies the member
as:

- `RetainedMount`;
- `Absent`;
- `DifferentMount`; or
- `ProbeFailed`.

It uses `statx(..., AT_SYMLINK_NOFOLLOW, ...)`, performs no allocation, and
opens no descriptor. It rejects empty, dot, dot-dot, or slash-containing
components. A change between ordinary and unique mount-ID kinds is treated as
capability drift rather than silently comparing unlike identities.

The SQLite VFS now requires statx mount-ID support at registration and fails
closed otherwise. Registration proves the main file is on the parent's mount.
Every existing main, journal, WAL, and SHM member must remain there at each
pathful safety frontier. Reproof of the retained parent descriptor also
re-captures and compares the parent mount identity.

### Adversarial proof

The shared directory-resolution test observes `/proc/bus`, a same-`st_dev`
distinct-mount witness on this host, and classifies it as `DifferentMount`.

The process-authority test enters a new user and mount namespace, makes the
mount tree private, registers the VFS, and bind-mounts a foreign regular file
over the reviewed WAL name. It independently proves that the mount-namespace
inode did not change. Direct VFS `xAccess` and `xOpen` calls reject the mounted
WAL, and the foreign bytes remain unchanged. It then bind-mounts the approved
main inode onto its own pathname. That second substitution preserves device,
inode, bytes, and mount-namespace inode; the public descriptor-rooted namespace
proof rejects it solely because the mount object changed. The cloudtainer
allowed both actual bind-mount witnesses; the skip path was not used for the
recorded release run.

## Audit and refactor work

The implementation was simplified while closing the defects:

- the retained main descriptor and all ownership/cleanup paths for it were
  removed;
- duplicated live-connection proof was centralized in
  `main_file_for_database_or_throw`;
- the product API now makes pre-open and live-handle evidence operations
  impossible to confuse by signature;
- the VFS reuses the existing process/thread-bound recursive SQLite database
  mutex guard rather than maintaining a weaker local duplicate;
- immutable logical and descriptor-rooted paths for all four family members are
  precomputed at registration, eliminating per-`xOpen` pathname allocation and
  cleanup while keeping pointer lifetime registration-bound;
- the unused `verify_private_parent_directory_or_throw` API was deleted;
- mount observation was moved into the existing shared POSIX directory-
  resolution owner rather than duplicated inside the VFS;
- the database-open source audit advanced to v16 and checks exact handle use,
  absence of a retained same-inode descriptor, mount-family freezing, and both
  kernel adversaries;
- the snapshot-seal audit now requires the active mount-family observer rather
  than a stale marker;
- the release verifier makes the rev0904 VFS, shared observer, adversarial
  tests, audits, and this document mandatory package members; and
- a fresh Clang registry exposed a separate test-harness publication race:
  the child created a readiness pathname before writing its status byte, while
  the parent treated existence alone as readiness. The parent now requires the
  exact one-byte control-record size before reading it.

## Validation

The release gate records the exact logs and machine-readable reports. The
principal results are:

- shared POSIX directory-resolution executable: **25/25** internal checks;
- SQLite process-authority executable: **90/90** internal checks;
- SQLite snapshot-seal source audit: **61/61**;
- replica database-open source audit v16: **34/34**;
- clean GCC 14 Debug registry: **221/221** tests;
- clean Clang 17 Debug registry after the harness correction: **221/221** tests;
- corrected payload-store control protocol: **64/64** parallel stress runs; and
- focused ASan/UBSan registry: **2/2** tests.

The release package is then verified both as a directory and after ZIP
extraction against its exact SHA-256 manifest, revision-scoped inventory,
active implementation projection, lineage, and required release gate.

The first Clang run is retained as negative evidence: 220 tests passed and the
payload-store test failed while opening a transient zero-byte readiness file.
Ten immediate serial reruns passed, which localized the defect to publication
ordering rather than product payload-store behavior. After the size-cutpoint
fix, 64 parallel executions and the complete Clang registry passed. The failure
was not erased or relabeled as environmental noise.

## What remains missing

This correction is material, but it does not turn the local product spine into
a complete synchronization product.

### Namespace authority remains cooperative, not hostile-root proof

The VFS narrows ambient pathname authority and rejects observed mount-family
substitution. It does not defeat a privileged actor that can continuously race
mounts or directory entries between observations and delegation, mutate the
process itself, replace procfs, or write raw storage. The mount check and opened-
file identity reproof reduce the attack surface; they are not a transaction over
kernel namespace state. A future design could move more of the Unix VFS into a
native descriptor-relative implementation and use `openat2` resolution policy
at each actual open, but that would be a substantial SQLite VFS ownership
commitment requiring separate lock, SHM, mmap, and durability validation.

### Traditional POSIX lock semantics still constrain composition

Rev0904 avoids introducing same-inode descriptors, but other code in the same
process could still open and close the database inode and thereby release
traditional locks. OFD locks have safer descriptor ownership semantics, yet
silently replacing SQLite's standard lock protocol would risk interoperability
with ordinary SQLite processes and would require a deliberately custom Unix VFS
plus cross-process compatibility analysis. The current product should treat the
process as one trusted lock-owning unit and keep database inode opens centralized.

### Separate SQLite stores are not one atomic deployment transaction

Replica, effect, membership, and anchor databases remain separate durability
domains. Bootstrap binding and recovery admission prevent many false
recompositions, but a live multi-store operation is not an atomic commit across
all stores. Durable intents, idempotent transitions, and reconciliation are the
right direction; claiming cross-store serializability would be false.

### The product surface is still incomplete

The central missing work remains a bounded long-running supervisor and a real
end-to-end causal synchronization loop: continuous scan/watch admission,
manifest exchange, chunked resumable transfer, conflict policy, crash-safe file
effects, retention/garbage collection, operator status and repair, resource
budgets, and deployment lifecycle. Privacy is also not yet a proved property.
Transport TLS and pseudonymous identifiers do not by themselves provide
traffic-analysis resistance, metadata minimization, unlinkability, at-rest
confidentiality, key rotation/revocation, or an explicit anonymity threat model.

### Platform scope is deliberately narrower

The descriptor-rooted product VFS depends on Linux procfs descriptor paths,
mount namespaces, and `statx` mount identity. It fails closed when the mount-ID
capability is absent. Portable POSIX and Windows support would require a
separate authority design rather than weakening the Linux proof to a path-only
fallback.

### Dependency hygiene is now an explicit release lane

The tree bundles SQLite 3.53.3. SQLite published 3.53.4 on 2026-07-24 as a patch
release for problems in the 3.53.0 through 3.53.3 line. Rev0904 does not mix a
dependency jump into this authority correction: doing so would make failures
harder to attribute. The next isolated dependency revision should verify the
upstream amalgamation hashes and rerun the full VFS, process-authority, database-
integrity, sanitizer, and release-package lanes before adoption.

## Research basis

Primary references used during the audit:

- Linux `fcntl` locking semantics:
  https://man7.org/linux/man-pages/man2/fcntl_locking.2.html
- Linux `statx` mount identity and flags:
  https://man7.org/linux/man-pages/man2/statx.2.html
- Linux `openat2` resolution constraints:
  https://man7.org/linux/man-pages/man2/openat2.2.html
- Linux pathname resolution model:
  https://man7.org/linux/man-pages/man7/path_resolution.7.html
- SQLite's explicit corruption warning for POSIX locks canceled by a separate
  `close()` and its Unix-driver workaround:
  https://www.sqlite.org/howtocorrupt.html#posix_close
- SQLite VFS interface:
  https://www.sqlite.org/vfs.html
- SQLite write-ahead logging and file family:
  https://www.sqlite.org/wal.html
- SQLite 3.53.4 release history and canonical amalgamation hashes:
  https://www.sqlite.org/changes.html
  https://www.sqlite.org/download.html

## Conclusion

Rev0904 corrects an implementation that had become sophisticated enough to hide
a basic kernel-lifetime mistake. The important lesson is architectural: a
retained descriptor is not automatically safer; its lock semantics must match
the subsystem that owns the inode. The revised VFS now keeps path authority
rooted, connection authority exact, mount-family identity explicit, and SQLite
record locks undisturbed by AnonSync's own evidence work. That is a stronger and
more honest local foundation for the still-unfinished convergence mission.
