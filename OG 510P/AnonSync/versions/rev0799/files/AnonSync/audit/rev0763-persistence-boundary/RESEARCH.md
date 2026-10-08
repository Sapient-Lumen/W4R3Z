# Persistence-boundary research notes — rev0763

Retrieved/reviewed 2026-07-13. Primary sources are preferred below.

## SQLite does not establish application-level semantic integrity

`PRAGMA integrity_check` and `quick_check` examine low-level database consistency and selected constraints. The documentation explicitly separates foreign-key checking into `foreign_key_check`; neither facility knows that a queue column must equal a field decoded from AnonSync's canonical envelope. A clean integrity check therefore cannot authorize a queue row. AnonSync must perform its own canonical-to-projection comparison on every authority-bearing read.

Sources:

- https://www.sqlite.org/pragma.html#pragma_integrity_check
- https://www.sqlite.org/pragma.html#pragma_foreign_key_check

## Typed extraction must precede C++ conversion

SQLite's `sqlite3_column_*` APIs can coerce storage classes. Reading a TEXT value with an integer accessor can create a plausible zero or truncated value instead of exposing malformed durable evidence. The API also documents pointer lifetime/conversion caveats for text/blob access. The persistence decoder should inspect `sqlite3_column_type`, preserve NULL distinctly, check lengths, and range-check signed values before conversion to unsigned C++ types.

Sources:

- https://www.sqlite.org/c3ref/column_blob.html
- https://www.sqlite.org/datatype3.html
- https://www.sqlite.org/stricttables.html

## Database atomicity is conditional, not a cross-resource transaction

SQLite's atomic-commit design depends on filesystem and device properties. It does not make an external payload spool and a SQLite row one atomic object. AnonSync still needs a documented ordering protocol and crash injection around temporary write, file synchronization, rename, parent-directory synchronization, database commit, and acknowledgement. WAL also has deployment constraints and is not a network-filesystem synchronization mechanism.

Sources:

- https://www.sqlite.org/atomiccommit.html
- https://www.sqlite.org/howtocorrupt.html
- https://www.sqlite.org/wal.html
- https://www.sqlite.org/lang_transaction.html

## Defensive database configuration helps but cannot replace verification

Defensive mode, untrusted schema handling, explicit application/schema identifiers, and page-level checks can reduce attack surface and catch classes of misuse. They do not prove that duplicated metadata agrees with canonical bytes. Triggers or deterministic functions may reject ordinary writes, but read-time verification remains necessary for old rows, corruption, migrations, and out-of-band writers.

Sources:

- https://www.sqlite.org/c3ref/c_dbconfig_defensive.html
- https://www.sqlite.org/pragma.html#pragma_trusted_schema
- https://www.sqlite.org/pragma.html#pragma_application_id
- https://www.sqlite.org/pragma.html#pragma_user_version
- https://www.sqlite.org/pragma.html#pragma_cell_size_check

## Design speculation

1. **Make projections disposable indexes.** Store canonical bytes plus their digest as evidence; regard peer/path/time columns as rebuildable acceleration data. A mismatch creates an immutable incident and blocks authority-bearing transitions. A separate, explicit repair tool can rebuild projections from canonical bytes after recording the contradiction.
2. **Use a verified-row capability.** Make raw row construction private. Read/claim/complete/recovery APIs should accept only a type obtainable through canonical decode plus complete projection comparison. This turns bypasses into compile errors rather than review conventions.
3. **Version the comparison set.** Envelope version and schema version jointly determine which fields must project. Keep a contiguous migration ledger and reject unknown pairs. Never interpret a missing post-migration field as a benign default.
4. **Add an executable crash oracle.** Model spool and SQLite operations as a small transition system, inject termination at each durable edge, reopen, and compare observable state with the oracle. Database tests alone cannot expose directory-sync or cross-resource ordering faults.
5. **Avoid schema-embedded envelope decoders for now.** A generated column or CHECK using an application-defined decoder is attractive, but it couples database readability to extension registration and trusted-schema policy. Application verification plus STRICT/range constraints is easier to audit and remains effective when opening legacy databases.
