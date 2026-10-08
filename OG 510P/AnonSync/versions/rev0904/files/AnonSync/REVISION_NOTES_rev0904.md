# AnonSync rev0904 revision notes

## Release identity

- Revision: `rev0904`
- Last externally linked package: `rev0898`
- Source-lineage parent: internal `rev0903` commit `e6f3202`
- Internal checkpoints folded into this release: `rev0899` through `rev0903`
- Theme: descriptor-rooted SQLite family authority, lock-safe live evidence,
  same-namespace mount-family fencing, and audit closure

## Product changes

1. Added a private descriptor-rooted SQLite VFS for every product database.
   Main, rollback-journal, WAL, and SHM operations are restricted to the exact
   reviewed family below one retained deployment directory descriptor.
2. Bound successful product connections to the exact private VFS instance and
   exact wrapped main `sqlite3_file`, not merely a VFS name or logical path.
3. Rejected anonymous SQLite file spill, unreviewed family names, named
   delete-on-close, lock-proxy paths, null-I/O closure, hard-linked sidecars,
   late hostile cleanup replacement, and inherited/mount-transition misuse.
4. Kept mount-namespace and procfs-bridge reproof at path-resolution frontiers
   rather than imposing procfs work on page, lock, or shared-memory hot paths.
5. Removed the independent retained main-file descriptor. Pre-open image reads
   are allowed only before that private VFS has a live file and are delegated to
   the bundled Unix VFS, preserving SQLite's same-process deferred-close lock
   workaround. Post-open reads and sync use the exact existing main-file object
   under the connection mutex.
6. Added a shared allocation-free `statx` relative mount observer and froze the
   parent mount identity. Every existing SQLite family member must remain on
   that exact mount, closing same-namespace bind-mount substitution that can
   preserve both mount-namespace inode and `st_dev`.
7. Made Linux statx mount identity a fail-closed product requirement for the
   descriptor-rooted VFS rather than silently falling back to device identity.

## Audit and refactor changes

- Centralized exact live-main-file proof in
  `main_file_for_database_or_throw`.
- Split pre-open and live-handle evidence APIs so lifecycle misuse is visible in
  the type/signature boundary.
- Removed the unused private-parent verification method.
- Moved mount-family observation into the shared POSIX directory-resolution
  owner instead of maintaining a VFS-local syscall variant.
- Reused the existing process/thread-bound recursive SQLite database mutex guard
  instead of keeping a second local mutex wrapper.
- Precomputed immutable logical and descriptor-rooted paths for the four family
  members, removing per-`xOpen` pathname allocation and ownership cleanup.
- Advanced the replica database-open audit to v16 with explicit lock-lifetime,
  exact-handle, mount-family, and adversarial process checks.
- Updated the snapshot-seal audit to require the active mount-family proof.
- Extended the release verifier's revision-scoped inventory for rev0904.
- Corrected a test-control publication race found by the fresh Clang lane:
  readiness-file existence was visible before its one-byte status was written,
  so the parent now treats exact one-byte size as the readiness cutpoint.

## Adversarial coverage added

- A real SQLite RESERVED lock is observed from a fork child before and after a
  delegated pre-open inspection and auxiliary VFS teardown. The lock remains
  held until the owning SQLite transaction/connection releases it.
- A same-namespace file bind mount places foreign bytes over the reviewed WAL
  name. The process proves its mount-namespace inode is unchanged; VFS
  `xAccess` and `xOpen` reject the substitution and preserve the foreign bytes.
- A second bind mount places the approved main inode over its own pathname,
  preserving bytes, device, inode, and namespace identity while changing only
  the mount object. The public namespace proof rejects that substitution.
- Shared resolution tests classify same-mount, absent, and same-device
  different-mount path components without opening the component.

## Validation summary

- POSIX directory-resolution checks: **25/25**
- SQLite process-authority checks: **90/90**
- SQLite snapshot-seal source audit: **61/61**
- Replica database-open policy audit v16: **34/34**
- Clean GCC 14 Debug CTest registry: **221/221**
- Clean Clang 17 Debug CTest registry after harness correction: **221/221**
- Corrected payload-store process-control stress: **64/64** parallel runs
- Focused ASan/UBSan CTest lane: **2/2**
- Directory package verifier: **required final publication check**
- ZIP package verifier: **required final publication check**

## Corrected severe failure mode

The unreleased descriptor-rooted implementation kept a second descriptor for
SQLite's main inode. With traditional POSIX record locks, closing any descriptor
for that inode can release all process-associated locks, including locks held
through SQLite's own descriptor. That evidence descriptor was therefore capable
of invalidating the concurrency proof it was meant to strengthen. Rev0904
removes it and adds a kernel-observed regression test.

## Explicit nonclaims and remaining work

- This is not proof against hostile root, raw block mutation, process injection,
  or an actor racing namespace transitions between every observation.
- Other same-process code must not independently open/close a database inode
  while SQLite lock ownership matters.
- Separate product SQLite stores are not atomic as one transaction.
- The implementation is intentionally Linux-specific and fails closed without
  procfs/statx mount authority.
- AnonSync still lacks the complete bounded supervisor, continuous causal
  synchronization loop, robust operator repair surface, full retention/GC and
  indexing, at-rest encryption/key lifecycle, and a formal anonymity and
  metadata threat model.
- The bundled SQLite 3.53.3 trails the 3.53.4 patch release published on
  2026-07-24. That dependency update should remain isolated and must rerun the
  VFS, process-authority, corruption, package, and sanitizer evidence lanes.

The detailed implementation, threat analysis, research, and future direction
are in
`SQLITE_DESCRIPTOR_ROOTED_LOCK_AND_MOUNT_FAMILY_AUTHORITY_AUDIT_rev0904.md`.
