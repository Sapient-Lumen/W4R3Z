# AnonSync rev0845 research notes

Accessed 2026-07-19. These primary or project-authoritative sources informed the
implementation and audit; citation does not imply that AnonSync implements every
mechanism described.

## Atomic private fixture directories

`mkdtemp(3)` creates a unique directory and specifies mode 0700. Rev0845 uses it
for local JSONL selftest workspaces so there is no create-public-then-chmod
window and no fixture bypass through a shared temporary parent.

- Linux man-pages, `mkdtemp(3)`:
  https://man7.org/linux/man-pages/man3/mkdtemp.3.html

## Modern descriptor-relative path resolution

`openat2(2)` can express resolution constraints including `RESOLVE_BENEATH`,
`RESOLVE_NO_MAGICLINKS`, `RESOLVE_NO_SYMLINKS`, and `RESOLVE_NO_XDEV`. The system
call appeared in Linux 5.6. The cloudtainer reports Linux 4.4, so rev0845 cannot
execute or claim that lane; the portable fallback performs explicit
component-by-component no-symlink traversal.

- Linux man-pages, `openat2(2)`:
  https://man7.org/linux/man-pages/man2/openat2.2.html

## Why mode checks are not process exclusivity

Linux capabilities such as `CAP_DAC_OVERRIDE` and `CAP_FOWNER` can bypass or
alter ordinary discretionary-access-control decisions. A mode/UID attestation
therefore cannot establish that no privileged or same-UID actor can mutate a
directory. Rev0845 names its guarantee “owner-controlled mutation surface” and
records an explicit non-claim of process exclusivity.

- Linux man-pages, `capabilities(7)`:
  https://man7.org/linux/man-pages/man7/capabilities.7.html

Kernel idmapped-mount documentation further shows that inode ownership and
userspace IDs can be interpreted through mappings. Exact sampled UID/GID values
are useful authority evidence in the current namespace, but they are not a
universal statement about all namespace or mount configurations.

- Linux kernel documentation, idmappings:
  https://docs.kernel.org/filesystems/idmappings.html

## Mount observations and their ceiling

`statvfs(3)` exposes filesystem statistics and mount flags such as `ST_RDONLY`.
Rev0845 freezes those observations and rejects a read-only mount, then treats any
later drift as authority loss. The filesystem ID and flags are observations;
they are not claimed as a unique, stable kernel mount identity.

- Linux man-pages, `statvfs(3)`:
  https://man7.org/linux/man-pages/man3/statvfs.3.html
- The Open Group, `<sys/statvfs.h>`:
  https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/sys_statvfs.h.html

## Permission semantics

`chmod(2)` documents ordinary permission-bit behavior and filesystem-dependent
handling of set-group-ID/sticky semantics. Rev0845 deliberately freezes the
complete sampled mode rather than claiming that a selected subset captures all
access policy.

- Linux man-pages, `chmod(2)`:
  https://man7.org/linux/man-pages/man2/chmod.2.html

## Engineering inference

The sources support three conclusions used in the audit:

1. exact descriptor/path/mode/mount reproof can detect sampled drift and fail
   closed;
2. it cannot prove an exclusive lease against same-UID, privileged, mapped, or
   racing actors; and
3. a stronger design should narrow mutation into a small broker and use modern
   resolution/mount-identity primitives where available.

That broker could combine a sealed descriptor with dropped capabilities,
Landlock, seccomp, resource ceilings, and typed commands. This is architectural
speculation, not a claim implemented by rev0845.
