# ADR 0119: derive private staging from attempt identity

Status: accepted

Date: 2026-08-21

## Decision

A synchronization attempt ID deterministically owns exactly one receive destination beneath the
namespace root:

```text
staging/attempt-<16 lowercase hexadecimal digits>.part
```

Callers do not supply that pathname. Preparation, commit, and discard all require the matching
`SyncNamespaceTransaction`. Preparation creates only strict owner-private namespace directories,
checks the immutable object's kind and per-object quotas, and refuses an existing destination so
`FileTransferManager` can retain its no-clobber receive contract.

Commit requires the derived path to name one owner-owned, mode-0600, singly linked regular file. It
checks exact size, hashes the completed file, and requires both to match the scheduler's canonical
object record. The existing exclusive object-publication primitive then copies, fsyncs, publishes,
and rechecks the digest-named object under the namespace transaction. Only after that succeeds is
the attempt path removed and its directory fsynced. Accepted HEAD and activation state are untouched.

Discard is idempotent for absence, but removes only the exact derived private regular file. Symlinks,
hard links, public files, foreign owners, directories, and other unexpected shapes fail closed and
remain undeleted.

## Consequences

An eventual file-transfer binding has no arbitrary destination authority, transport completion is
not sufficient evidence by itself, and a fenced attempt has an exact cleanup target. A commit that
lands the immutable object but cannot remove staging is safely retryable; an unreferenced object is
not publication or activation authority.

This slice does not yet bind a toxcore offer/file number to an attempt, reserve aggregate in-flight
staging bytes, persist attempts across restart, or invoke scheduler completion after object commit.
Those remain mandatory before Gate 3 carries product traffic.
