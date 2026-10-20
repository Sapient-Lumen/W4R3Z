# ADR 0139: Bind deterministic directory revisions as treepack-v1

Date: 2026-08-24

Status: accepted

## Context

IoTox already publishes, transfers, accepts, and explicitly activates immutable regular-file
revisions. The preserved toxsync component also contains a deterministic treepack format, but using
it as a product directory surface requires more than recognizing packed bytes. The signed HEAD must
state what the artifact means; local source traversal and unpacking need bounded filesystem policy;
and a power cut must not confuse signed activation truth with an incomplete directory projection.

Directory activation is also not an update installer. Received path names, executable bits, or a
successful transfer must not grant arbitrary filesystem placement or execution authority.

## Decision

1. Allocate signed HEAD engine value `3` to `treepack-v1`. Engine selection remains immutable local
   namespace policy and is authenticated by the existing stable-device-signed HEAD. IoTox never
   sniffs an artifact to choose its meaning.
2. `sync-namespace-template-tree` emits the canonical manual-activation tree policy.
   `sync-publish NAMESPACE PATH` accepts a directory only for that engine. File and range-v1
   namespaces retain their existing regular-file contract.
3. The product adapter reuses the preserved canonical treepack codec. It bounds the complete encoded
   artifact, entry count, path length, individual file size, and in-memory path-sort population from
   namespace quotas plus fixed product ceilings. It does not spill through a system temporary
   directory.
4. Publication accepts only an absolute owner-controlled directory tree. The root and every entry
   must belong to the effective UID and have no group/other write bit. Only real directories and
   single-link regular files are admitted; symlinks, hard links, and special files fail before HEAD
   publication.
5. Tree artifacts still receive the canonical range-v1 index as their manifest and travel through
   the existing whole-object synchronization path. `treepack-v1` does not imply range reuse,
   content-v2, path-level merging, or multi-source scheduling.
6. Signed activation state remains authoritative. It is committed only after artifact digest and
   artifact/index semantics verify. Directory materialization is a derived post-commit projection:
   unpack into one exact private staging directory, deterministically repack it, require the signed
   artifact digest, fsync files and directories, freeze files to `0400`/`0500` and directories to
   `0500`, rename the complete revision, then atomically replace the relative `current` symlink.
7. An exact activation retry re-verifies and reconciles the projection even when signed activation
   state already names that revision. This closes the power-cut seam between durable signed state
   and derived materialization.
8. Under the namespace transaction, recovery classifies every entry below
   `materialized-trees/revisions` before mutation. Only exact canonical revision directories and
   `.REVISION.part.PID.SEQUENCE` staging directories are accepted. Selected subtrees are completely
   validated before deletion. Abandoned staging is removed and fsynced; after `current` is durable,
   every other derived revision is pruned, leaving one current projection.
9. There is no `sync-rollback`. Restoring prior content requires publishing it as a new higher,
   exactly parent-linked signed generation.

## Consequences

The same signed namespace/authority/object machinery now carries deterministic directories without a
second trust root or an implicit extraction decision. Content convergence and signed activation can
survive an interrupted projection because exact retry reconstructs derived state from the verified
immutable object. Derived trees do not multiply with retained signed revisions; retention pins object
identity, not materialized copies.

The boundary deliberately excludes arbitrary destination paths, symlinks, device nodes, ownership
metadata, setuid/setgid bits, ACL/xattr preservation, sparse-file semantics, automatic execution,
directory merging, conflict resolution, and rollback by lowering generation. A hostile process with
the same UID can still race owner-local paths; IoTox's Unix account boundary is not a defense against
an equally privileged local attacker.
