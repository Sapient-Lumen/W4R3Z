# Rev0826 research notes

Rev0826 treats pathname observations as evidence that expires unless the exact
kernel object remains owned. The local defect showed why: rev0825 preflighted a
receipt path, committed SQLite reset, then reopened the path. Renaming the
verified parent and creating a replacement redirected the receipt into the
replacement directory.

## Descriptor identity and create-new publication

Linux `open(2)` documents that an open file descriptor refers to an open file
description and remains attached to that object even when the pathname is
removed or changed. Rev0826 therefore retains the verified parent directory
file descriptor across the reset commit rather than retaining only its path:
<https://man7.org/linux/man-pages/man2/open.2.html>

Linux `rename(2)` documents `RENAME_NOREPLACE` as refusing to overwrite an
existing destination. It remains the create-new namespace linearization point;
preflight and final-name inspection are denial evidence, not reservation:
<https://man7.org/linux/man-pages/man2/rename.2.html>

`openat2(2)` offers useful future resolution constraints such as
`RESOLVE_BENEATH`, `RESOLVE_NO_SYMLINKS`, and `RESOLVE_NO_XDEV`. These can
reduce traversal ambiguity, but they do not preserve identity across a later
SQLite commit. A retained descriptor is still required:
<https://man7.org/linux/man-pages/man2/openat2.2.html>

`O_TMPFILE` plus `linkat(AT_EMPTY_PATH)` could remove visible temporary names on
supporting Linux filesystems. The cloudtainer probe used the required
`O_RDWR|O_TMPFILE` flags on its overlay mount and received `EISDIR`; this lane
is therefore not available here. The manual also makes filesystem support and
`AT_EMPTY_PATH` privilege/availability constraints explicit. No production
change is based on this unavailable probe:
<https://man7.org/linux/man-pages/man2/open.2.html>
<https://man7.org/linux/man-pages/man2/link.2.html>

Both rename/link manuals warn that NFS can report an error even after the server
performed the operation. Rev0826 consequently makes no network-filesystem claim
that a returned error proves non-publication.

## Fork lineage and its limit

The first draft used raw PID equality. The audit rejected that wording and the
implementation now reuses AnonSync's PID-plus-fork-lineage process-incarnation
token. This prevents a fork child from exercising a capability minted by its
parent in the focused single-threaded oracle.

That is not an async-signal-safe post-fork API for a multithreaded process. POSIX
requires the child of a multithreaded `fork()` to restrict itself to
async-signal-safe operations until `exec`; this C++ API allocates, throws, and
uses library machinery. The supported architectural direction is to avoid
using inherited C++ capabilities in such a child and to reconstruct authority
after `exec`:
<https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html>

## Next experiments

1. Rename the generic process-incarnation primitive out of the SQLite namespace
   so file, network, and database capabilities share a neutral owner without an
   architectural naming leak.
2. Add a deterministic hook exactly between retained-parent revalidation and
   temp reservation, and model a same-UID namespace attacker at every later
   frontier. Classify effects rather than promising isolation.
3. Prototype `openat2` resolution as an optional Linux hardening lane, preserving
   the existing component-walk fallback and testing mount/symlink compatibility.
4. Extend the reset crash oracle across SQLite VFS commit cutpoints and prepared
   publication cutpoints. Recovery must infer durable state from artifacts, not
   process-local return values.
5. Continue the independent convergence algebra and privacy/key-lifecycle work;
   this revision proves a local evidence-publication boundary, not anonymity or
   distributed convergence.
