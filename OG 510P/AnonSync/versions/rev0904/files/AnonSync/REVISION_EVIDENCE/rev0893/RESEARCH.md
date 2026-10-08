# rev0893 research record

Primary references informed the cutpoints but do not prove the implementation.

## Linux `openat2(2)`

<https://man7.org/linux/man-pages/man2/openat2.2.html>

`RESOLVE_BENEATH`, `RESOLVE_NO_MAGICLINKS`, `RESOLVE_NO_SYMLINKS`, and
`RESOLVE_NO_XDEV` can constrain descriptor-relative path resolution. Rev0893
uses them only through the project's already observed capability state and
retains a fail-closed weaker-capability path rather than inferring support from
kernel version.

## Linux `fsync(2)`

<https://man7.org/linux/man-pages/man2/fsync.2.html>

File synchronization does not by itself establish directory-entry durability.
The publisher and reconciliation path therefore keep file and directory
synchronization as separate cutpoints.

## RFC 6920 — Naming Things with Hashes

<https://www.rfc-editor.org/rfc/rfc6920>

The RFC motivates hash-derived object names and verification of referenced
bytes. Rev0893 does not implement the RFC URI format; it uses a local full
lowercase SHA-256 basename and verifies bytes against that name. The current
namespace has no algorithm tag or agility mechanism.

## SQLite write-ahead logging

<https://sqlite.org/wal.html>

SQLite WAL can provide durable database transaction semantics but cannot make a
filesystem content publication atomic with an outbox transaction. Rev0893
therefore permits payload-without-operation and treats operation-without-payload
as nonterminal unavailable content that consumes no claim authority.

## SQLite PRAGMA documentation

<https://sqlite.org/pragma.html>

SQLite durability settings remain owned by the existing SQLite profile and
connection authorities. The payload directory is not presented as a second
SQLite database, and no cross-resource commit claim is made.

## Speculation and next research

A production indexed content owner should keep a versioned append-only catalog
or SQLite index, but only as acceleration. It should bind root identity,
identity-marker generation, digest, exact size, stable file observations, and a
catalog generation; use one writer or explicit lease; and continuously compare
generated scenarios against the rev0893 full-scan oracle.

Garbage collection requires explicit reachability evidence from canonical
operations, active outbox attempts, staged effects, receipts, repair state,
checkpoints, and offline/revoked replicas. A summary of current outbox rows is
not enough. Content encryption and anonymizing transport are separate concerns:
digest names, sizes, timing, and access patterns still expose local metadata.
