# AnonSync rev0842 research notes

Accessed 2026-07-19. These sources informed the audit and forward-looking design. They do
not imply that AnonSync implements every cited mechanism or guarantee.

## File and directory durability

Linux `fsync(2)` documents an important distinction: synchronizing a file does not
necessarily persist the directory entry naming that file. An explicit fsync of the
containing directory is needed for the directory entry. This matters for a recovery
journal created before a later ledger rename: the whole ordering must be treated as one
crash protocol, not inferred from the file contents alone.

- Linux man-pages, `fsync(2)`:
  https://man7.org/linux/man-pages/man2/fsync.2.html
- Linux man-pages, `rename(2)`:
  https://man7.org/linux/man-pages/man2/rename.2.html
- SQLite atomic commit assumptions:
  https://www.sqlite.org/atomiccommit.html
- SQLite WAL behavior:
  https://www.sqlite.org/wal.html

## Path resolution and namespace confinement

`O_NOFOLLOW` applies to the final pathname component; it is not an all-component
confinement mechanism. Linux `openat2(2)` exposes explicit resolution policies including
`RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`, `RESOLVE_NO_SYMLINKS`, and
`RESOLVE_NO_MAGICLINKS`. A future descriptor-owned namespace layer can use these to make
its path policy executable. The ordinary path-resolution documentation is useful for
understanding why parent components, mount points, and magic links need separate
consideration.

- Linux man-pages, `openat2(2)`:
  https://man7.org/linux/man-pages/man2/openat2.2.html
- Linux man-pages, `path_resolution(7)`:
  https://man7.org/linux/man-pages/man7/path_resolution.7.html

Rev0842 uses final-component no-follow, opened-object `fstat`, bounded EOF reads, and
before/after identity and metadata checks. It does not claim `openat2` confinement or
hostile parent-directory control.

## Locale-free and deterministic machine bytes

C++ `std::to_chars` provides direct locale-independent integral conversion. Rev0842
factors this into a shared dependency-light primitive used by frozen publications and
hash material.

JSON Canonicalization Scheme exists because equivalent JSON values can have multiple byte
representations while signatures require invariant bytes. Rev0842 does not implement JCS
generally. It uses fixed local encoders and, for current effect-intent v3 material,
named length framing. Legacy newline formats remain readable only after delimiter-bearing
controls are excluded.

- Current C++ working draft, character conversion:
  https://eel.is/c++draft/charconv.to.chars
- RFC 8785, JSON Canonicalization Scheme:
  https://www.rfc-editor.org/rfc/rfc8785.html
- RFC 8259, JSON grammar:
  https://www.rfc-editor.org/rfc/rfc8259.html

## Convergence as a semantic property

CRDT literature frames convergence around deterministic state agreement after replicas
receive equivalent updates. Local authentication, hash chains, and durable recovery are
valuable prerequisites but cannot define the result of concurrent update/delete/rename
histories. AnonSync still needs an executable operation model and generated trace oracle.

- Preguiça, Baquero, Shapiro, “Conflict-free Replicated Data Types”:
  https://arxiv.org/abs/1805.06358
- Kleppmann and Beresford, “A Conflict-Free Replicated JSON Datatype”:
  https://arxiv.org/abs/1608.03960

## Authentication versus privacy and recovery after compromise

The Messaging Layer Security architecture separates the group cryptographic protocol
from delivery, authentication infrastructure, multi-device synchronization, metadata
policy, and application integration. It is a useful warning for AnonSync: a signed
manifest or transition authenticates a statement, but does not by itself provide payload
confidentiality, anonymity, forward secrecy, post-compromise recovery, or metadata
protection.

- RFC 9420, Messaging Layer Security protocol:
  https://www.rfc-editor.org/rfc/rfc9420.html
- RFC 9750, Messaging Layer Security architecture:
  https://www.rfc-editor.org/rfc/rfc9750.html

## Hostile parsing needs layered isolation

Linux kernel documentation explicitly warns that seccomp filtering is not a complete
sandbox. Landlock can add self-imposed filesystem restrictions. A future verification
worker should combine descriptor-only input, namespaces, resource limits, wall-clock
supervision, seccomp, Landlock where supported, and a bounded response protocol.

- Linux seccomp filter documentation:
  https://docs.kernel.org/userspace-api/seccomp_filter.html
- Linux Landlock documentation:
  https://docs.kernel.org/userspace-api/landlock.html

## Speculation

A coherent destination is a two-plane design:

- a data plane of encrypted, content-addressed chunks that never decides conflicts;
- a control plane of small authenticated causal operations carrying object generation,
  device/key epoch, membership, revocation, and explicit conflict semantics.

Each local durable step would consume one frozen authority capsule and produce a
digest-bound recovery receipt. A deterministic model would serve as protocol
specification, generated-history oracle, and compatibility test. Directory-descriptor
owners and disposable verification workers would keep hostile namespace and parsing
behavior outside the semantic core.
