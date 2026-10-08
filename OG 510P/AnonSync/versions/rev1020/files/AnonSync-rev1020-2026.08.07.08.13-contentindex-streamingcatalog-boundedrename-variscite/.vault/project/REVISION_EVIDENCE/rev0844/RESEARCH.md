# AnonSync rev0844 research notes

Accessed 2026-07-19. These primary or project-authoritative sources informed the
implementation and audit; citation does not imply that AnonSync implements every
mechanism described.

## File and directory durability

Linux `fsync(2)` explicitly notes that synchronizing a file does not necessarily
synchronize the directory entry containing it; an explicit fsync of the
directory is needed. Rev0844 therefore places directory barriers after journal
publication, ledger rename, and journal retirement.

- Linux man-pages, `fsync(2)`:
  https://man7.org/linux/man-pages/man2/fsync.2.html

SQLite's atomic-commit analysis is useful because it separates file-content,
directory-entry, filesystem, flush, and storage-device assumptions rather than
treating “fsync happened” as a universal proof. Rev0844 adopts that distinction
for the surrounding JSONL protocol, while making no all-filesystem claim.

- SQLite, Atomic Commit In SQLite:
  https://www.sqlite.org/atomiccommit.html

## Descriptor-relative namespace operations

`renameat(2)` and the `*at` family resolve relative names against retained
directory descriptors. Rename replacement is atomic as a namespace operation,
but it is not a conditional compare-and-swap on inode identity. Rev0844 uses
`renameat`, `linkat`, `unlinkat`, `openat`, and `fstatat` beneath one retained
parent, while keeping concurrent same-directory writers outside the proved
boundary.

- Linux man-pages, `rename(2)` / `renameat(2)`:
  https://man7.org/linux/man-pages/man2/rename.2.html

`openat2(2)` can express stronger resolution constraints such as beneath-only,
no symbolic links, no magic links, and optional mount confinement. The current
Linux 4.4 host predates `openat2`, so rev0844 cannot claim runtime coverage.

- Linux man-pages, `openat2(2)`:
  https://man7.org/linux/man-pages/man2/openat2.2.html

## No-overwrite publication

The journal staging inode is published with a hard-link edge rather than rename.
The relevant property is local: creating the destination link fails when that
name already exists, avoiding silent replacement of an existing recovery
witness. The temporary two-link topology is explicitly modeled and verified
before staging-name retirement.

## Speculation

A stronger mutation boundary could combine a sealed directory descriptor with a
small disposable helper process. The parent would own path policy and process
supervision; the helper would expose only typed operations such as
`publish_journal`, `replace_ledger`, and `retire_exact_witness`, with CPU, memory,
wall-clock, descriptor, syscall, and filesystem limits. This would not eliminate
filesystem races by itself, but it would make directory write authority narrow,
auditable, and separable from hostile document parsing.

At the product layer, the local recovery receipt should eventually be the
implementation artifact of a deterministic replicated-operation model, not the
source of distributed semantics. A content-addressed encrypted data plane plus a
small authenticated causal control plane remains a plausible architecture.
