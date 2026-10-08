# AnonSync rev0879 revision notes

## Purpose

Rev0879 closes rev0878's explicit stable-root gap for the POSIX immutable File
effect path and refactors the older local JSONL directory owner onto the same
capability implementation. It also adds a focused root-authority audit and
adversarial live, restart, and descendant-policy runtime coverage.

## Primary parent

The lineage parent is the user-provided
`AnonSync-rev0878-2026.07.22.07.35-effectterminal-cutpointguard-payloadpreflight-liveauthority.zip`.

## Production C++ changes

### Shared retained directory capability

New `SyncDirectoryAuthority` is move-only, process-incarnation-bound,
thread-incarnation-bound, and POSIX-only. It opens an absolute directory by
component with no-symlink inspection, retains the terminal descriptor, freezes
identity/credential/mode/mount observations, enforces owner-controlled mutation
policy, and permanently revokes itself after any failed descriptor/path reproof.

Its canonical SHA-256 attestation digest binds device, inode, ownership,
effective credentials, mode, filesystem ID, mount flags, and filesystem name
limits.

### Local JSONL directory-owner refactor

`LocalJsonlReplayDirectoryAuthority` is now a thin compatibility facade over the
shared owner. It retains its existing public shape and namespace friend access,
but no longer contains duplicate traversal, descriptor, attestation, process,
thread, or revocation state machines.

### Descriptor-relative atomic publication and reconciliation

The atomic file owner adds POSIX rooted create-new and restart-reconciliation
APIs. They accept a retained root capability and a strict canonical relative
path, duplicate the verified root descriptor, walk child directories with
`fstatat`/`openat` no-follow identity checks, and re-prove the root and terminal
parent around mutation and durability cutpoints.

Each descendant directory must remain on the retained root device, be owned by
the retained effective UID, grant owner read/write/search, and deny group/other
write. Rejection occurs before temporary inode reservation.

The existing absolute-path and new rooted paths share one publication syscall
state machine and one immutable reconciliation state machine; no second atomic
write protocol was copied.

### Root-bound file-effect schema

`SyncReplicaFileEffectSqliteOwner` now retains the root capability for its
lifetime. Exact schema advances to version 2 and stores a mandatory root
authority digest. Publication and complete-cutpoint digest domains advance to v2
and bind normalized root path plus authority digest.

Every public owner operation verifies the root before database work and around
mutable/precommit cutpoints. POSIX materialization constructs only a canonical
relative operation path and uses rooted reconciliation/publication; it no longer
reconstructs an absolute destination from root text.

Automatic migration from schema v1 is intentionally refused because v1 never
recorded root object identity. Binding old effects to whichever object currently
occupies the path would manufacture authority.

## Runtime tests

Expanded tests prove:

- deterministic shared attestation hashing and identity sensitivity;
- existing JSONL move, mode, symlink, thread, and fork capability behavior after
  refactor;
- live same-path root replacement rejects before stage mutation;
- the replacement tree receives no temporary or final effect bytes;
- observed root contradiction is sticky after path restoration;
- a fresh owner against the restored exact root sees the unchanged cutpoint and
  can complete publication;
- restart against a same-path replacement root rejects the persisted authority
  digest without changing the original database;
- a group/other-writable descendant rejects before temp reservation, leaves the
  effect staged and retryable, and succeeds only after owner-controlled mode is
  restored; and
- existing immutable publication/reconciliation and effect-terminal tests remain
  green.

## Audit/refactor work

`tools/audit_sync_effect_root_authority.py` inventories the generic capability,
JSONL delegation, strict relative traversal, descendant policy, shared atomic
state machines, schema-v2 binding, SQLite proof ordering, adversarial runtime
surface, CMake ownership, and package inventory. It explicitly identifies its
scope as lexical hygiene, not semantic proof.

The atomic-publication audit was adapted to the shared verifier callback rather
than retaining a false assumption that only absolute-path parent verification
could be correct. The local JSONL crash audit now follows the generic source and
checks that the compatibility wrapper contains no duplicate security state.

The design record documents Linux `openat2`, `RESOLVE_NO_XDEV`, and `statx` mount
IDs as future hardening. The portable `st_dev` policy does not detect a
same-device bind mount.

## Compatibility

- File-effect SQLite exact schema is version 2.
- Schema-v1 effect databases fail closed and require an explicit future
  operator-authorized migration.
- Causal SQLite remains schema version 5.
- File-delivery wire protocol remains version 1.
- Existing local JSONL callers retain their compatibility class.
- Windows remains path-bound and does not receive retained-root parity in this
  revision.

## Deliberate nonclaims

Rev0879 does not claim mount-namespace containment, same-UID exclusivity,
protection from privileged local actors, cross-database/filesystem atomicity,
Windows parity, an authorized root-rebind protocol, a shipped replica service,
production-scale indexing, ordinary update/delete/rename effects, complete
retry/dead-letter policy, membership/key lifecycle, compaction, anonymity,
externally trusted provenance, or formal proof.

The file-effect owner remains an O(history) correctness oracle.
