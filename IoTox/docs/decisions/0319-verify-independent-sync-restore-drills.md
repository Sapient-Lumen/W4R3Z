# ADR 0319: Verify independent synchronization restore drills

- Status: accepted and implemented
- Date: 2026-09-03

## Context

IoTox can synchronize a bounded private Linux tree, preserve signed history, repair missing content,
and restore a historical projection forward. None of those operations proves that an independently
versioned backup can recover the owner's data after every live IoTox node is unavailable. The
precious-data graduation plan therefore requires a restore drill that does not consult a live IoTox
tree or store.

A human can compare two directories with general Unix tools, but the result may silently ignore the
same ownership, mode, link, sparse-file, xattr, and conflict-projection boundaries that IoTox itself
enforces. Calling such a comparison “verified” would be weaker than the synchronization contract.

## Decision

Add one local, read-only entrance:

```text
iotox sync-recovery-verify BACKUP_ROOT RESTORED_ROOT \
  [MAXIMUM_BYTES [MAXIMUM_ENTRIES]]
```

Both operands must be existing, normalized, absolute, non-root directories. Their canonical paths
must be disjoint; neither may contain the other or resolve to the same directory. The default scan
ceilings are 64 MiB and 4,096 entries. An operator may supply explicit nonzero ceilings up to 2^60
bytes and 2^32 entries.

The command models each tree as a tree-v2 `owner-mode-v2` projection. It reuses ADR 0318's bounded
filesystem-contract walk to require private Agent-user ownership, regular files and directories,
single-link dense files, byte-exact case-sensitive names, and no ACL/xattr, symlink, special-file,
or ASCII case-collision state. An existing top-level `.iotox-conflicts` projection is refused rather
than skipped: the owner must resolve or separately archive conflict alternatives before claiming an
exact restore.

The verifier alternates two complete scans of each tree and repeats the filesystem-contract check.
Either tree changing between the two observations refuses. It compares the canonical relative path,
entry kind, file bytes, and exact private owner mode of every selected entry, then reports both
manifest digests and bounded counts. Exit zero means an exact match under that model. A well-formed
mismatch and every inspection refusal return the ordinary refusal status rather than a plausible
success.

The report is strict `iotox-sync-recovery-verify-v1`. Paths are hex encoded. It states explicitly:

```text
filesystem-contract=ready
stable-double-scan=ready
iotox-live-state-read=0
backup-independence=not-assessed
restore-provenance=not-assessed
```

The command opens neither Agent configuration nor control socket, namespace policy, identity,
authority, witness, object store, worktree journal, or synchronized live tree. It writes neither
input. Selecting the backup generation and restored target remains an operator act.

## Consequences

Four owned checks bring the direct registry to 831 and the stable command registry to 200
spellings. They cover an exact nested restore including owner modes, a content-and-mode mismatch,
canonical alias/containment refusal, unresolved conflict-projection refusal, and the public CLI
report/nonclaims. Final qualification passes 831/831 direct checks in 37.27 seconds, all 55 GCC
CTest entries in 54.82 seconds, and all 70 Clang ASan/UBSan entries in 64.01 seconds. Both complete
CTest surfaces retain only the five explicit host-cgroup/PSI skips.

This closes only the exact external-tree comparison mechanism inside the recovery-rehearsal gate.
It does not prove that the backup is versioned, offline, immutable, complete, authentic, recent,
restored onto different hardware, or outside every writer's authority. Alternating double scans are
not an atomic cross-filesystem snapshot and cannot rule out an ABA change. The command does not
recreate device/namespace authority, reseed nodes, retire old writers, rehearse loss of one or all
nodes, validate backup software, certify storage durability, or make synchronization history a
backup. Those operator and end-to-end gates remain open.
