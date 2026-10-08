# Rev0981 audit handoff

## Scope

Rev0981 makes the schema-v7 database recovery epoch operable without starting synchronization. It adds descriptor-rooted forensic inspection, exact-token epoch advancement, and one deployment singleton shared by retained service, one-shot sync, inspection, and recovery advance.

## Primary correction

The first implementation acquired the singleton but opened writable SQLite before discovering that a recovery token was stale. The retained ceremony now parses canonically, opens the existing primary database through the exact read-only rooted VFS, attests deployment binding, compares incarnation, epoch, and complete cutpoint, closes the forensic handle, and only then opens writable SQLite for an independent `BEGIN IMMEDIATE` reproof. Malformed, foreign, future, and consumed tokens therefore cannot trigger WAL recovery, sidecar creation, checkpointing, migration, or another writer-side effect.

## Adjacent audit/refactor

The recovery transition originally built owning response strings after durable commit. Rev0981 now constructs the complete result before `COMMIT` and statically requires a nothrow move afterward, removing an avoidable exception-after-success ambiguity. The one-shot singleton negative control now uses a missing native-I2P private-destination file, proving deployment ownership wins before an authority-bearing route file can be opened. Shared manifest-to-primary-database targeting was split into explicit writer and forensic read-only seams, and private WAL indexing is selected before the first page read.

## Runtime proof

The 105-check real-process oracle fingerprints exact SQLite-family membership, mode, size, and SHA-256 around inspection, malformed input, three canonical stale expectations, exact advancement, and consumed-token reuse. It hides unrelated payload, rooted-file, and catalog stores and compares all non-lineage status after recovery. The final database-open policy audit passed 48/48 and the wrapper-aware structural audit passed 385/385.

## Nonclaim

Database incarnation and recovery epoch remain inside SQLite. Exact whole-image rollback restores both. Rev0981 does not validate backup bytes, replace the database family, supply an external monotonic anchor, reset retention age, or grant collection, reclaim, rename, or unlink authority.
