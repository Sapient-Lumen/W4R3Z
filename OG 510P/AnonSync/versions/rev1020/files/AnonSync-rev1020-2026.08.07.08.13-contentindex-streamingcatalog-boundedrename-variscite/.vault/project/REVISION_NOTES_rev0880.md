# AnonSync rev0880 revision notes

## Purpose

Rev0880 closes rev0879's explicit same-device mount-boundary gap in the retained
POSIX effect-root path. It replaces three partly duplicated directory-component
walkers with one capability-aware syscall owner, freezes the actually observed
Linux resolution capability for one live authority, and adds adversarial runtime
and source-audit evidence. During the refactor it also corrects a rejected-path
file-descriptor leak in root-descriptor duplication.

## Primary parent

The exact lineage parent is the user-provided
`AnonSync-rev0879-2026.07.22.09.21-rootcapability-descendantpolicy-jsonlrefactor-mountsentinel.zip`,
whose SHA-256 is
`30ac76aa6b592458906aa41c60c345ad364314bc2d6ca2d3f21562fdc248af3a`.

## Production C++ changes

### One POSIX directory-resolution owner

New `sync_posix_directory_resolution.{hpp,cpp}` owns component opening,
no-follow identity verification, Linux capability probing, mount-ID capture, and
cross-mount rejection for the retained-root effect path. Absolute authority
opening, rooted atomic publication, and legacy absolute atomic publication now
delegate component resolution to this implementation rather than maintaining
three security-sensitive syscall loops.

Domain-specific policy remains with its owner. `SyncDirectoryAuthority` still
owns root identity, credentials, permissions, process/thread affinity, and
sticky revocation. Atomic publication still owns temporary inode, rename,
reconciliation, and durability cutpoints. The new component owner only resolves
and proves directory descriptors.

### Observed capability, not kernel-version inference

The live capability is one of:

- portable device/inode verification;
- Linux `statx` mount-ID verification;
- Linux `openat2` with `RESOLVE_NO_XDEV`; or
- both Linux mechanisms.

Only an `ENOSYS` syscall result, or successful `statx` without the requested
mount-ID bit in `stx_mask`, is treated as explicit feature unavailability.
Permission denial, invalid-argument responses, I/O failures, and other
unexpected probe results fail closed. This avoids silently weakening policy
under seccomp, LSM, ABI, programming, or kernel faults.

For the Linux no-cross-mount path, each component is opened with
`RESOLVE_BENEATH | RESOLVE_NO_MAGICLINKS | RESOLVE_NO_SYMLINKS |
RESOLVE_NO_XDEV`. `EXDEV` is surfaced as a mount crossing. `EAGAIN` is retried
with a fixed bound of eight attempts and cannot become an unbounded liveness
loop.

### Mount identity reproof

Where `statx` reports mount identity, the retained root and every opened
component must report the same mount ID. `STATX_MNT_ID_UNIQUE` is preferred when
reported; otherwise the older namespace-scoped mount ID is used. The returned
`stx_mask`, not header availability or kernel generation, determines whether
the observation exists.

`SyncDirectoryAuthority` freezes its resolution capability and live mount
identity, re-proves both its retained descriptor and the path currently reached,
and permanently revokes on contradiction. Atomic publication carries those
observations with its duplicated root descriptor.

The durable v1 root-attestation digest is intentionally unchanged. Linux mount
IDs are useful live-process evidence, but even the unique form is guaranteed
only while the system is running. Treating it as restart-stable identity would
make a reboot look like durable authority corruption. A future boot-epoch and
operator-authorized root-rebind protocol must solve that separately.

### Same-device mount crossing corrected

Rev0879 compared `st_dev` for descendants. Distinct mounts can expose the same
device number, so this was not a mount-boundary proof and could not exclude bind
mounts or other same-device submounts. On capable Linux systems, rev0880 rejects
such traversal in the kernel with `RESOLVE_NO_XDEV` and independently verifies
mount identity after open where `statx` supplies it. Other POSIX systems retain
the explicitly named portable baseline and its narrower claim.

### Descriptor-duplication leak corrected

The atomic publication bridge duplicated the verified root descriptor and then
re-proved authority before returning ownership. If that second proof threw, the
new descriptor had no owner and leaked. The exceptional path now closes the
duplicate before rethrowing. The source audit binds that ownership transfer;
ASan/UBSan and leak detection cover the affected focused runtime surface, but a
deterministic race injection at the exact post-duplication proof window is not
claimed.

## Runtime tests

The new deterministic test matrix proves:

- exact capability names and composition;
- `openat2` success and explicit `ENOSYS` fallback;
- fatal classification for `EINVAL`, `EPERM`, and `EIO` rather than silent
  downgrade;
- `statx` success only when `stx_mask` reports the requested mount identity;
- absolute root and ordinary descendant opening through the shared owner;
- capability preservation through move-only authority transfer; and
- on this cloudtainer, rejection of `/proc/bus` reached from `/proc` even though
  the two directories have equal `st_dev`, with independently observed distinct
  unique `statx` mount IDs.

The host-specific witness is capability-gated and reports an explicit skip on a
portable host rather than manufacturing support. Existing atomic publication,
prepared publication, reconciliation, file-effect owner, delivery service, and
local JSONL authority tests remain green.

## Audit/refactor work

`tools/audit_sync_mount_boundary_authority.py` inventories capability probing,
error classification, `openat2` resolve flags, bounded retry, `statx` mask
checking, frozen authority evidence, descriptor ownership, shared traversal,
adversarial runtime coverage, CMake ownership, package inventory, and explicit
nonclaims. It states that lexical inspection is architecture hygiene rather
than behavioral proof.

The existing root-authority, atomic-publication, and local-JSONL audits were
updated to follow the new syscall owner and to reject reintroduction of parallel
component loops. The refactor deliberately does not absorb member-file create,
rename, unlink, SQLite path, or JSONL namespace contracts into a generic
filesystem abstraction.

## Validation

Fresh cloudtainer evidence records:

- GCC 14.2 Debug all-target build, 373 initial Ninja steps, and zero final
  compile/link work;
- 188/188 registered tests in one CTest invocation;
- 58/58 audit-named registered tests;
- seven focused GCC Debug executables, 257/257 checks;
- 20 iterations across three authority executables, 60/60 runs and
  2,000/2,000 checks;
- seven focused Clang 17 Release `-Werror` executables, 257/257 checks;
- seven focused GCC 14 ASan/UBSan executables, 257/257 checks, leak detection
  enabled, with bundled SQLite C instrumented; and
- six focused source audits totaling 206/206 checks.

Full-project Clang, full-project sanitizer, ThreadSanitizer, and Windows runtime
lanes are not claimed.

## Compatibility and deliberate nonclaims

- File-effect SQLite exact schema remains version 2.
- Causal SQLite remains schema version 5.
- File-delivery wire protocol remains version 1.
- The durable root-attestation digest remains v1 and does not contain ephemeral
  mount IDs.
- The local JSONL compatibility facade remains intact.
- Linux capability probing is runtime-observed; non-Linux POSIX keeps the
  device/inode baseline.

Rev0880 does not claim restart-stable mount identity, protection against mount
namespace changes performed by the same or privileged actor, same-UID
exclusivity, Windows retained-root parity, an authorized root-rebind protocol,
production use of the newer owners by `anonsync_core`, production-scale indexed
ownership, update/delete/rename effects, complete retry/dead-letter policy,
membership/key lifecycle, causal compaction/rejoin, anonymity or traffic
analysis resistance, externally trusted provenance, or formal proof. The
file-effect and causal owners remain O(history) correctness oracles.
