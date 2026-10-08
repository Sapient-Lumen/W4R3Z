# rev0880 compact audit record

## Load-bearing correction

Rev0879 retained an exact root descriptor but used `st_dev` as the descendant
mount fence. Device identity is not mount identity: a bind mount or another
submount may expose the same device number. Rev0880 introduces one shared POSIX
directory-resolution owner. On capable Linux systems it uses
`openat2(RESOLVE_NO_XDEV)` to reject every mount crossing during kernel path
resolution and uses `statx` mount IDs as an independent post-open identity
witness. The cloudtainer runtime proves a real `/proc` to `/proc/bus` crossing
with equal `st_dev` and distinct unique mount IDs is rejected.

## Capability truthfulness

The owner probes the running environment rather than inferring behavior from a
kernel release. Only `ENOSYS`, or successful `statx` without the requested mask
bit, permits fallback. `EINVAL`, `EPERM`, `EIO`, and other unexpected outcomes
are fatal. This preserves the project's central rule that unavailable evidence
may narrow a claim but anomalous evidence cannot silently manufacture weaker
authority.

The live capability and mount ID are frozen and re-proved. They remain outside
the durable attestation digest because unique mount IDs are guaranteed only for
the running system, not across restart. This is a deliberate boundary, not a
missing hash field.

## Refactor and ownership correction

Absolute root opening, rooted publication traversal, and legacy absolute
publication traversal now use one component syscall owner. Root credentials,
mode and revocation remain in `SyncDirectoryAuthority`; atomic mutation and
durability remain in the publication owner. The refactor removes duplicate
security logic without creating an oversized generic filesystem state machine.

Review also found a descriptor leak between root duplication and the second
authority proof. The bridge now closes the duplicate on every exceptional
post-duplication path before rethrowing.

## Evidence hierarchy

The 33-check mount audit and the adapted root, atomic, JSONL, thread, and
delivery audits are lexical architecture inventories. They are not behavioral
or formal proof. Load-bearing evidence is the 19-check deterministic/runtime
mount corpus, the complete 188-test registry, independent compiler lane,
instrumented sanitizer lane, and repeated authority stress.

## Remaining severe boundaries

The shipped `anonsync_core` executable still does not compose the newer causal,
transport, file-effect, and retained-root owners. Mount IDs are not durable
across reboot, and rev0880 has no boot-epoch/root-rebind ceremony. Same-UID or
privileged actors and mount-namespace mutation remain outside the local
exclusivity claim. Non-Linux POSIX retains only the device/inode baseline.
Windows parity, production indexing, ordinary update/delete/rename effects,
complete retry/dead-letter policy, membership and key lifecycle, compaction,
anonymity, externally signed provenance, and formal proof remain open.
