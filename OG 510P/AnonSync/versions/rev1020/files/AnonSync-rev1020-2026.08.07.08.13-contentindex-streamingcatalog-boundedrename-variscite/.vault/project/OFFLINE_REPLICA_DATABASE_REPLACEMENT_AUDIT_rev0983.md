# Offline replica-database replacement audit — rev0983

## Product reason

Rev0982 made one primary replica database portable as a bounded, immutable,
deployment-bound SQLite artifact. That was not yet a recovery runbook: an
operator could inspect the artifact and advance lineage, but no retained C++
owner could safely install the artifact while preserving the displaced logical
database.

Rev0983 adds one separate offline replacement owner. It is deliberately not a
method on the backup creator. Backup creation remains immutable and
non-restoring; replacement is an explicit destructive ceremony with its own
current-state expectation and rollback destination.

## Authority order

The replacement command performs this order while the deployment singleton is
held:

1. Parse canonical absolute candidate and rollback paths. Treat each selection
   as the exact four-name SQLite family consisting of the main name plus
   `-journal`, `-wal`, and `-shm`. Require the two families to be disjoint and
   require every member to remain outside the manifest, every active SQLite
   family, payload storage, and synchronized roots.
2. Preflight the complete rollback output family create-new before retaining as
   much as 512 MiB of candidate state. A deterministic existing main or sidecar
   conflict is rejected before expensive capture or publication.
3. Capture and completely detached-verify the candidate artifact before any
   namespace mutation. The retained resident seal, not a later pathname lookup,
   is the replacement source capability.
4. Open the active primary replica through the descriptor-rooted forensic
   profile, require the operator's exact incarnation/epoch/cutpoint expectation,
   and bracket one transactionally pinned logical capture.
5. Compare candidate and active SQLite page sizes before publishing rollback
   state. SQLite documents that a backup into a WAL destination cannot change
   page size; failing early avoids a rollback artifact for an incompatible
   candidate.
6. Repeat the complete rollback-family preflight at the last non-mutating
   cutpoint, then publish the displaced logical image create-new as an
   owner-only, sidecar-free rollback artifact and independently reopen it.
7. Reopen the active database through the existing descriptor-rooted writable
   VFS, re-prove that it still equals the rollback source, and copy the retained
   candidate through the centralized bounded SQLite backup owner.
8. Require the active logical cutpoint to equal the validated candidate exactly.
9. Advance recovery epoch and state generation through the existing exact
   `BEGIN IMMEDIATE` transition.
10. Close the writer and independently reopen the active deployment through the
    forensic profile before reporting success.

The main-name create-new publication is the final atomic no-replace authority.
POSIX does not provide one atomic reservation for all four deterministic family
names, so rev0983 does not claim to defeat a concurrent hostile same-UID writer
that creates a sidecar after the final preflight. The mandatory postpublication
sealed reopen rejects such a resulting non-sidecar-free artifact; it cannot
retroactively make the four-name publication atomic.

## Why logical SQLite replacement, not raw family rename

The live database uses WAL. SQLite explicitly treats the database and WAL as one
atomic state and warns against separating or ad-hoc copying those files. A raw
main-file rename would need a second, subtle family-swap protocol and would risk
combining a candidate main image with stale WAL/SHM state. The retained design
instead asks SQLite to replace the destination logically under its own write
transaction while the existing descriptor-rooted VFS owns every active-family
open.

The SQLite online-backup API also defines failure before completed copy as a
rolled-back destination transaction. Rev0983 centralizes both private snapshot
capture and named-database replacement in one fixed-size page-step owner, with
an exact page-size preflight for the named WAL destination.

Primary references:

- https://sqlite.org/backup.html
- https://sqlite.org/c3ref/backup_finish.html
- https://sqlite.org/wal.html

## Rollback meaning

The rollback artifact preserves the complete displaced *logical primary replica
database* in canonical standalone SQLite form. It does not preserve raw inode,
WAL, SHM, journal, allocation, or byte-for-byte family identity. It is suitable
as an input to the same detached inspector and replacement ceremony.

The artifact does not include payload bytes, the folder catalog, membership,
effects, anchors, synchronized files, TLS key material, or service state. It is
not a whole-share backup.

## Crash boundary

Success is emitted only after replacement, recovery-epoch advance, and an
independent final reopen. A process or machine failure can still occur after
SQLite commits the logical replacement but before the epoch transition. The
create-new rollback artifact remains available. The active database must remain
offline; `database-recovery-inspect` identifies the visible cutpoint and
`database-recovery-advance` completes the mandatory transition when the exact
candidate cutpoint is present. Rev0983 does not claim an external durable action
receipt or automatic idempotent resume across that cutpoint.

## Retention-age boundary

Every durable retention mark binds exact database lineage and causal roots. A
replacement followed by the mandatory recovery-epoch transition changes the
source cutpoint used by future collection authority. Existing mark age must not
be reused when continuity is uncertain. Rev0983 still performs no payload
collection, reclaim, rename, or unlink.

## Audit/refactor

The first namespace audit found that artifact policy compared only main
pathnames. A rollback selection could be the candidate's `-wal`, `-shm`, or
`-journal` name, and a pre-existing rollback sidecar could force failure only
after the main rollback artifact was published. The shared artifact helper now
projects all four deterministic family names, applies full-family overlap and
root exclusion, and performs early plus final output-family preflight. The real
process oracle covers candidate/rollback family overlap, a payload root occupying
an artifact sidecar name, and deterministic backup and rollback sidecars without
main-name publication.

The existing SQLite live-backup loop previously admitted only an empty private
in-memory destination. Rev0983 refactors that loop into one implementation with
two explicit destination profiles:

- empty private in-memory capture; and
- existing named writable replacement.

The second profile requires a named writable FULLMUTEX handle, no active
transaction, and an exact pre-copy page-size match. Focused tests prove success,
rollback after an injected nonterminal step failure, page-size rejection before
mutation, read-only rejection, and private-destination rejection. No second raw
`sqlite3_backup_*` loop was added.

The same audit found a terminal-cutpoint defect in the pre-existing observer
shape. SQLite releases/completes the destination write transaction when
`sqlite3_backup_step()` returns `SQLITE_DONE`; invoking a throwable observer
after that result could therefore report operation failure after a named
destination had already committed. The retained observer now runs only after
validated nonterminal `SQLITE_OK` steps, where it remains a true between-effects
cutpoint followed by source-pin reproof. A one-step named replacement supplies a
throwing observer and proves that terminal completion never invokes it.

Shared artifact path validation, compact cutpoint projection, detached schema
attestation, and resident-seal inspection were also moved to one internal header
used by both backup and replacement owners. This removes duplicated authority
spelling without exposing a second CLI-level owner.

## Nonclaims

Rev0983 does not provide:

- whole-share backup or restore;
- payload restoration;
- cross-database transactional restore;
- external anti-rollback authority;
- raw SQLite-family byte preservation;
- online replacement while the service runs;
- an idempotent durable replacement receipt; or
- retention-policy execution or garbage collection.

## Next safe edge

The next recovery edge is a durable, external-to-the-replaced-database action
receipt that can resume or classify the narrow post-copy/pre-epoch crash window
without guessing. Product work should then return to end-user restore and
first-uninstall workflow qualification rather than expanding database ceremony
for its own sake.
