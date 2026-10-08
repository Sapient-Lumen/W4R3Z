# AnonSync rev0904 audit

## Heart of the mission

AnonSync exists to preserve bounded, exact, identity-bearing evidence so that
independent replicas can converge on authorized state after crashes, retries,
concurrency, partial failure, and adversarial recomposition. Byte movement is a
mechanism, not the mission. Observation must never silently become authority,
and every mutable path must remain subordinate to retained capabilities and
revalidated evidence.

## Correction delivered

Rev0904 carries each selected deployment directory into a private SQLite VFS,
restricts the main database and its rollback-journal/WAL/SHM family to reviewed
relative names, and attests both the exact public VFS and exact wrapped main
`sqlite3_file` before product ownership proceeds.

The audit found a severe flaw in the unreleased design: retaining a second file
descriptor for SQLite's main inode could release all traditional process-owned
POSIX locks for that inode when the auxiliary descriptor closed. The correction
removes that descriptor. Pre-open reads are delegated to SQLite's bundled Unix
VFS before one private authority has a live file; live evidence reads and syncs
use the already-open exact main file while holding AnonSync's SQLite mutex guard.
A fork child observes a real RESERVED lock before and after inspection and VFS
teardown, proving the lock survives until the owning transaction releases it.

A second authority gap allowed bind mounts introduced inside an already approved
mount namespace. Namespace identity and `st_dev` do not distinguish every mount
object. Rev0904 freezes Linux `statx` mount identity for the retained parent and
requires every existing SQLite family member to remain on that mount. Real
adversaries bind-mount foreign bytes over the WAL and bind-mount the approved
main inode over its own pathname; both are rejected, including the second case
where device, inode, bytes, and namespace inode all remain unchanged.

## Audit/refactor delivered

The VFS now reuses the existing process/thread-affine recursive SQLite mutex
guard, centralizes exact live-main proof, separates pre-open from live-handle
evidence APIs, and moves mount observation into the shared POSIX directory
authority. Four immutable logical and descriptor-rooted family paths are
precomputed at registration, so noexcept VFS callbacks do not allocate or own
transient pathname storage. Exact source inventories were advanced rather than
relaxed.

A fresh Clang 17 registry then found a separate inherited-process test race. The
child created the final readiness pathname before writing its one-byte status,
while the parent treated existence alone as publication. The parent now requires
exact one-byte size as the readiness cutpoint. The initial 220/221 Clang result
is retained; after correction, 64 parallel stress executions and both complete
compiler registries passed.

## Validation

- GCC 14 Debug registry: **221/221**.
- Clang 17 Debug registry: **221/221** after the recorded correction.
- Initial Clang negative evidence: **220/221**, exact readiness race retained.
- Corrected parallel readiness stress: **64/64**.
- POSIX directory-resolution direct checks: **25/25**.
- SQLite process-authority direct checks: **90/90**.
- Database-open policy audit v16: **34/34**.
- SQLite snapshot-seal source audit: **61/61**.
- Focused GCC 14 ASan/UBSan lane: **2/2**.
- Parent rev0898 package self-verification: **30/30**.

## Remaining mission gaps

The local authority spine is stronger, but the product remains incomplete. The
highest-value next work is a bounded long-running supervisor and end-to-end
causal synchronization loop: continuous scan/watch admission, manifest exchange,
chunked resumable transfer, conflict policy, crash-safe effects, durable repair,
retention/garbage collection, indexing, and resource budgets. Separate SQLite
stores are not one atomic transaction. At-rest encryption, key lifecycle, and a
formal anonymity/metadata threat model remain absent. This Linux-specific VFS is
not hostile-root proof and does not make namespace observations transactional
against a continuously racing privileged actor.

The detailed implementation and threat analysis are in
`SQLITE_DESCRIPTOR_ROOTED_LOCK_AND_MOUNT_FAMILY_AUTHORITY_AUDIT_rev0904.md`.
