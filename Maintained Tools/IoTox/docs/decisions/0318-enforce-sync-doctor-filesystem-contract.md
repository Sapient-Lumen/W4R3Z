# ADR 0318: Enforce the synchronization-doctor filesystem contract

- Status: accepted and implemented
- Date: 2026-09-03

## Context

IoTox's bounded synchronization model represents Linux regular-file bytes, directories, and a small
owner-mode vocabulary. It does not represent ACLs, arbitrary extended attributes, sparse allocation,
timestamps, cross-user ownership, links, or special files. The production tree scanners already
rejected several of those shapes, and the doctor documented the transformations, but it did not
machine-check every unsupported filesystem semantic. A plausible `decision=ready` could therefore
hide metadata or allocation behavior that would not survive projection.

The trust-graduation plan requires unsupported semantics to be implemented or loudly preflighted and
refused. It does not permit a successful scan to imply cross-platform or backup fidelity.

## Decision

Before and after the existing production source scan, both `sync-doctor` and
`sync-doctor-configured` perform one bounded, read-only filesystem-contract walk. The root and every
ordinary entry must be owned by the Agent user and not group/world writable. Only directories and
owner-readable, single-link regular files are admitted. Symlinks and every special-file type are
refused.

The walk uses `llistxattr(2)` without following links and refuses any named extended attribute; this
also catches POSIX ACL state on Linux filesystems that encode it as an xattr. Each nonempty regular
file is descriptor-pinned and inspected with `SEEK_HOLE`; a filesystem without that query falls back
to allocated-block accounting. A discovered hole, or an allocation for which dense storage cannot
be established, is refused. Paths are inserted into a bounded locale-independent ASCII-folded set,
and a collision is refused before the ordinary scanner can call it portable. The walk observes the
same namespace object ceiling as the selected production scanner, so the preflight itself cannot
grow without the source quota.

Tree-v2's generated `.iotox-conflicts` projection is excluded from this input check because it is a
derived output, not user-authored synchronized state. The ordinary tree remains byte-exact and
case-sensitive. Unicode folding and a case-insensitive destination are not inferred.

The pre-creation report advances from strict v1 to strict v3, and the configured report advances
from strict v2 to strict v4. The prior records remain historical evidence; they are not silently
extended. Both new records contain these closed fields:

```text
filesystem-contract=ready
path-model=byte-exact-case-sensitive-required
ascii-case-collisions=refused
ownership=agent-owner-required-local-owner-projected
hard-links=refused
symlinks=refused
special-files=refused
acl-xattrs=refused
sparse-layout=refused
timestamps=not-preserved
```

The output is deliberately asymmetric: ownership and timestamps exist on every ordinary source, so
it names their projection semantics instead of pretending they can be absent. Directory modes remain
normalized and regular-file owner bits remain governed by `executable-v1` or `owner-mode-v2`.

## Consequences

Two owned checks bring the direct registry to 827. Existing CLI checks also freeze the new v3/v4
headers so an old strict decoder cannot mistake the expanded grammar for v1/v2. One uses a real user
xattr, hole-only sparse file, hard-link pair, and FIFO; each must refuse. The other creates two legal
Linux names that differ only by ASCII case and requires refusal. Existing success coverage now
requires all ten contract lines, while the prior symlink and owner/mode checks remain in force.

Final qualification passes 827/827 direct checks in 35.28 seconds, all 55 GCC CTest entries in
73.39 seconds, and all 70 Clang ASan/UBSan entries in 85.20 seconds. The two complete CTest surfaces
retain only the five explicit host-cgroup/PSI skips.

This is point-in-time Linux preflight. A source may change after inspection, so operators must run
the configured doctor on every member and repeat it after material filesystem changes. The check
does not preserve timestamps, xattrs, ACLs, sparse layout, links, special files, or foreign
ownership; support case-insensitive or Unicode-normalizing filesystems; certify `fsync`; reserve
space; verify destination hardware; or turn synchronized history into an independent backup.
