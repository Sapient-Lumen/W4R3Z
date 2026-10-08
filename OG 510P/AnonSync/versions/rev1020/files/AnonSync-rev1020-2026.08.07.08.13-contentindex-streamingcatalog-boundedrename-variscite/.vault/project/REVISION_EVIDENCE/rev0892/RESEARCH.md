# Rev0892 primary-source research

The implementation and audit were checked against primary specifications and
official documentation. These sources informed design constraints; they are not
substitutes for executable proof.

## Unknown code and callback retirement

- C++ Core Guidelines CP.22:
  https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#cp22-never-call-unknown-code-while-holding-a-lock-eg-a-callback

The guidance warns against invoking unknown code while holding synchronization
authority. AnonSync's boundary is stricter: arbitrary payload callbacks are also
unsafe while a durable outbox claim exists, even when the SQLite mutex is no
longer held, because exceptions, blocking, reentrancy, and mutable external state
can make the claim's outcome ambiguous. Rev0892 replaces the callback with a
validated value object.

## Content identity

- RFC 6920, Naming Things with Hashes:
  https://www.rfc-editor.org/rfc/rfc6920
- NIST FIPS 180-4, Secure Hash Standard:
  https://csrc.nist.gov/pubs/fips/180-4/upd1/final

These sources support hash-addressed content naming and SHA-256 calculation.
AnonSync still treats a digest as content identity evidence, not authorization,
freshness, provenance, availability, confidentiality, or collision-proof
mathematical identity.

## SQLite transaction, durability, and failure-domain limits

- Isolation: https://sqlite.org/isolation.html
- Transactions and `BEGIN IMMEDIATE`: https://sqlite.org/lang_transaction.html
- WAL: https://sqlite.org/wal.html
- `PRAGMA synchronous`: https://sqlite.org/pragma.html#pragma_synchronous
- Atomic commit: https://sqlite.org/atomiccommit.html
- `SQLITE_FCNTL_HAS_MOVED`:
  https://sqlite.org/c3ref/c_fcntl_begin_atomic_write.html#sqlitefcntlhasmoved

`BEGIN IMMEDIATE` supplies one-database writer serialization. SQLite documents
its own atomic-commit assumptions and durability modes, but it does not create an
atomic transaction across two independent database files or prove storage-media
provenance. Rev0892 therefore exposes the membership-first/anchor-second crash
gap and requires reconciliation rather than claiming two-database atomicity.

## Rollback protection and stronger roots

- The Update Framework specification:
  https://theupdateframework.github.io/specification/latest/
- Trusted Computing Group TPM 2.0 Library Specification:
  https://trustedcomputinggroup.org/resource/tpm-library-specification/

TUF's rollback model depends on trusted retained state outside newly supplied
metadata. Rev0892 implements that separation at the application level with a
second append-only SQLite owner, but two same-host files can still be rolled back
together. TPM monotonic/NV facilities illustrate a stronger class of root; a
remote witness, transparency checkpoint, or separately administered append-only
service may also be appropriate. No such stronger root is implemented here.

## Design inference

A second durable store materially improves crash accounting and detects rollback
of only the membership database relative to the retained anchor. It is not
independent merely because it has a different pathname, inode, or SQLite
connection. Failure-domain independence requires separate trust, rollback,
backup, credential, and administration boundaries, plus authenticated update
provenance and recovery policy.
