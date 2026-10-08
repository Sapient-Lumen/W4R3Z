# rev0880 primary-source research and inference

Research was rechecked online on 2026-07-22 against primary Linux interface and
kernel documentation.

- Linux `openat2(2)`: https://man7.org/linux/man-pages/man2/openat2.2.html
  `RESOLVE_BENEATH` constrains descendant resolution;
  `RESOLVE_NO_MAGICLINKS` and `RESOLVE_NO_SYMLINKS` prevent link-mediated
  redirection; `RESOLVE_NO_XDEV` disallows traversal of all mount points,
  including bind mounts. The interface documents `EXDEV` for a rejected mount
  crossing and `EAGAIN` for a lookup race that callers may retry.
- Linux `statx(2)`: https://man7.org/linux/man-pages/man2/statx.2.html
  Callers must inspect `stx_mask` because requested fields may be absent.
  `STATX_MNT_ID` identifies the containing mount; `STATX_MNT_ID_UNIQUE` is
  guaranteed not to be reused while the system is running, which is a live
  lifetime guarantee rather than reboot-stable identity.
- Linux VFS pathname lookup:
  https://docs.kernel.org/filesystems/path-lookup.html
  Mount-point crossing and concurrent namespace mutation are explicit parts of
  path resolution. The VFS can abort beneath/in-root lookup with `EAGAIN` when
  mount-table movement prevents a safe proof.
- Linux mount namespaces:
  https://man7.org/linux/man-pages/man7/mount_namespaces.7.html
  Mount lists are namespace-local and may be changed independently after
  namespace creation. A path or filesystem device number alone therefore does
  not bind one immutable mount topology.
- Linux filesystem mount API:
  https://docs.kernel.org/filesystems/mount_api.html
  Mounts are first-class kernel objects, reinforcing the distinction between a
  filesystem/inode observation and the mount through which it is reached.

## Applied inference

The strongest available live Linux policy is layered rather than substitutive:
use `openat2` to prevent crossing during lookup, then compare `statx` mount
identity where available, while retaining descriptor/inode and owner/mode
proofs. Capability must be based on observed syscall behavior, not headers or
kernel version. Unexpected probe failures must fail closed because seccomp,
LSM, ABI mismatch, or programming errors are not evidence that a security
feature is safely absent.

## Speculation and next work

A restart-safe mount authority likely needs an explicit boot epoch plus an
operator-authorized root-rebind record that binds the new live root capability
to durable prior history. Persisting a raw mount ID without that ceremony would
confuse a reboot with corruption. Linux `statmount`/`listmount` may eventually
provide richer live topology evidence, but they do not by themselves create a
stable cross-boot identity or protect against a privileged namespace mutator.

The larger product milestone remains an executable service that composes one
canonical operation, authenticated channel, bounded payload, retained-root
publication, effect-terminal receipt, and sender settlement. Further local
hardening is useful only if that composition path begins consuming it.
