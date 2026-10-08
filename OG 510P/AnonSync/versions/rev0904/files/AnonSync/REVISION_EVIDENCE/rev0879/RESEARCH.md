# rev0879 primary-source research and inference

- Linux `open(2)`: https://man7.org/linux/man-pages/man2/open.2.html
  Directory file descriptors provide stable references even if a directory is
  renamed and avoid races caused by repeatedly resolving a pathname prefix.
- Linux `openat2(2)`: https://man7.org/linux/man-pages/man2/openat2.2.html
  `RESOLVE_IN_ROOT`, `RESOLVE_BENEATH`, `RESOLVE_NO_SYMLINKS`, and
  `RESOLVE_NO_XDEV` describe a future Linux-specific tightening of the portable
  component-by-component `fstatat`/`openat` implementation.
- Linux `path_resolution(7)`: https://man7.org/linux/man-pages/man7/path_resolution.7.html
  Mount-point traversal requires an explicit policy; lexical containment is not
  namespace containment.
- Linux `statx(2)`: https://man7.org/linux/man-pages/man2/statx.2.html
  `STATX_MNT_ID` and `STATX_MNT_ID_UNIQUE` can distinguish mount identities that
  a plain `st_dev` comparison may not.
- Linux `rename(2)`: https://man7.org/linux/man-pages/man2/rename.2.html
  Atomic name replacement/no-replace semantics do not prove the identity or
  durability of the containing directory by themselves.
- Linux `fsync(2)`: https://man7.org/linux/man-pages/man2/fsync.2.html
  Synchronizing file content does not necessarily synchronize the directory
  entry, so effect-terminal evidence includes parent-directory durability.
- Linux VFS path lookup: https://docs.kernel.org/filesystems/path-lookup.html
  Path lookup is a sequence of component resolutions under concurrent namespace
  mutation, reinforcing the need for descriptor-relative identity checks.

Inference: the next Linux hardening should add a reviewed `openat2` backend with
`RESOLVE_BENEATH|RESOLVE_NO_SYMLINKS|RESOLVE_NO_MAGICLINKS|RESOLVE_NO_XDEV`, plus
mount-ID attestation where supported, while retaining the current portable
backend as a differential oracle. This would narrow mount traversal but would
not create exclusivity against same-UID or privileged actors.
