# Offline replica-database backup artifact audit — rev0982

## Product reason

Rev0980 gave the primary replica database an incarnation and recovery epoch.
Rev0981 made the epoch observable and explicitly advanceable. Neither revision
created a supported artifact that an owner could copy away, inspect later, and
identify as one exact AnonSync replica cutpoint. That left the recovery command
without the first half of an operator runbook.

Rev0982 adds that bounded prerequisite. It is intentionally narrower than a
share backup: it captures the primary replica SQLite database only. Payload
bytes, the folder catalog, effect database, TLS membership and anchor databases,
certificates, keys, rooted files, and network state are not included. The
artifact is useful for preserving causal/evidence/lineage state, but it cannot
restore a working share by itself.

## Operator surface

The shipping C++ command now exposes:

```text
anonsync_sync database-backup-create \
  --manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE

anonsync_sync database-backup-inspect \
  --manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE
```

Both commands claim the existing deployment singleton before any selected
SQLite family or backup artifact is opened. They are offline operations: a live
service, one-shot synchronization process, another recovery command, or another
backup command for the same deployment excludes them.

The create command publishes only at an absent destination. Repeating create at
an existing path fails rather than replacing or trusting that path. The inspect
command never opens the active replica database and remains usable after that
entire SQLite family has been moved away.

## Creation authority order

`SyncReplicaDatabaseBackupOwner` is the shipping authority owner. The CLI only
parses options and renders JSON. The owner performs this sequence:

1. Validate one canonical absolute artifact path.
2. Reject the deployment manifest, every configured SQLite main/journal/WAL/SHM
   family member, and any path at or below payload storage or synchronized files.
3. Perform a no-symlink, create-new publication preflight before allocating the
   resident copy.
4. Open the active primary replica database through the rev0981 descriptor-
   rooted forensic profile and attest the deployment binding.
5. Restore and validate the complete current schema, then immediately reduce
   the full causal model to one compact exact cutpoint witness.
6. Use the retained bounded SQLite backup/seal owner to copy one transactionally
   consistent logical database image into private process memory.
7. Canonicalize and verify standalone rollback-journal geometry, SHA-256, page
   bounds, schema v7, deployment binding, and the complete replica cutpoint on a
   filename-free read-only deserialization.
8. Repeat the live-source complete-schema observation and rooted database reproof.
9. Require the compact before, captured, and after witnesses to match exactly.
10. Publish the exact resident bytes atomically and create-new at mode 0600.
11. Close the source authority, reopen the durable artifact through its own
    no-symlink, single-link, sidecar-free path, and repeat digest, geometry,
    binding, schema, and cutpoint proof.

The online-backup primitive is not treated as publication authority. It produces
one private logical snapshot. The existing atomic-file owner supplies the final
namespace and durability boundary.

## Boundedness and memory refactor

The artifact ceiling is 512 MiB and 262,144 SQLite pages, both below the generic
untrusted-snapshot maximum. The current implementation is deliberately resident,
not streaming. Deserialization owns another private SQLite buffer, so the
ceiling is a per-artifact input bound rather than a promise that total process
RSS stays below 512 MiB.

The first composed implementation retained complete `SyncReplicaSqliteSnapshot`
objects for the source-before, captured, and source-after observations while the
resident SQLite image was also alive. Those snapshots contain the entire causal
operation graph and outbox. Rev0982 now releases each graph immediately after
full validation and retains only a compact exact witness containing lineage,
generations, canonical state digests, historical-pin digest, and the final
cutpoint digest. This removes avoidable multi-graph peak memory without replacing
complete schema restoration with a metadata shortcut.

## Detached read-only SQLite correction

The retained sealed-snapshot owner opens a filename-free database with
`SQLITE_DESERIALIZE_READONLY`. SQLite's `sqlite3_db_readonly()` nevertheless
reports an in-memory database as read/write. Treating that introspection result
as the authority made the first backup inspection reject a database whose writes
were in fact denied.

Rev0982 keeps named forensic files on the existing
`sqlite3_db_readonly()==1` gate. A separate detached-image gate proves the
properties that matter:

- the main database has no filename and uses MEMORY journaling;
- the hardened connection remains `query_only`;
- after temporarily removing that connection-level belt inside a savepoint, a
  main-schema `CREATE TABLE` still fails with `SQLITE_READONLY`;
- the savepoint is rolled back and `query_only` is restored;
- the exact deployment binding and complete replica snapshot are attested in
  one deferred transaction.

A focused regression records the counterintuitive SQLite behavior explicitly:
`sqlite3_db_readonly()` returns zero while an actual write fails read-only.
This prevents a future cleanup from reintroducing the false oracle.

Official SQLite references consulted:

- https://sqlite.org/backup.html
- https://sqlite.org/c3ref/backup_finish.html
- https://sqlite.org/capi3ref.html (deserialize, filename, and read-only APIs)
- https://sqlite.org/forum/info/80e765eb24d26f01

## Namespace and artifact properties

Artifact inspection uses the existing sealed snapshot reader, which rejects:

- symlinks or symlinked traversal;
- non-regular or multiply linked files;
- `-wal`, `-shm`, or `-journal` siblings;
- unstable inode, size, mode, link count, mtime, or ctime observations;
- empty, oversized, malformed, noncanonical, or WAL-format images;
- changed resident bytes or geometry;
- wrong application ID, deployment binding, manifest identity, database path,
  folder, actor, schema, causal state, or cutpoint.

SHA-256 here is an integrity and identity check, not a signature or an external
anti-rollback anchor. Anyone able to replace the manifest and artifact together
is outside this in-database authority model.

## Failure and completion semantics

Create-new prevents an existing destination from being overwritten. A process
failure before final link leaves no visible artifact name. A failure after the
link but before JSON output can make command completion observationally unknown;
`database-backup-inspect` is the recovery oracle. Inspection is idempotent and
performs no repair or replacement.

The source database family is fingerprinted by the real-process oracle across
bad-path rejection and successful creation. The artifact is independently
reopened, then inspected again with the live source family absent. A damaged
artifact fails without creating sidecars or changing its bytes.

## What this does not prove

Rev0982 does **not**:

- back up payload bytes, current rooted files, folder catalog state, TLS
  membership/anchor state, effect receipts, credentials, or configuration;
- replace, restore, roll back, rename, quarantine, or unlink an active database;
- provide an external monotonic counter or exact-image rollback detection;
- authenticate an artifact for transport across an untrusted channel;
- stream artifacts larger than the resident 512 MiB product ceiling;
- reset durable retention-mark age after a restore;
- define retention duration, quota, ENOSPC, minimum versions, or collection;
- make one replica-database artifact a complete Resilio-style share backup.

## Next safe edge

The next recovery slice should be a separate offline database-family replacement
owner, not an extension of the backup creator. It must preserve the displaced
family for rollback, validate the candidate before mutation, acquire the same
deployment singleton, publish through exact rooted no-symlink authority, require
post-replacement `database-recovery-advance`, and conservatively reset retained
mark age whenever continuity is uncertain. Only then is there a supported
primary-database restore ceremony. A complete share backup remains a later
multi-store product design.
