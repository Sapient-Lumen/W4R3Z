# Rev0891 primary-source research

The implementation and audit were checked against primary documentation rather
than treating source vocabulary as proof.

## SQLite durability and transaction authority

- SQLite `PRAGMA synchronous`: https://sqlite.org/pragma.html#pragma_synchronous
  - In WAL mode, `FULL` adds a sync after each commit and is documented as durable across power loss.
  - In rollback-journal modes, `EXTRA` adds directory synchronization after journal deletion; rev0891 therefore does not treat `FULL` as the strongest rollback-journal publication policy.
- SQLite WAL: https://sqlite.org/wal.html
- SQLite transactions and `BEGIN IMMEDIATE`: https://sqlite.org/lang_transaction.html
- SQLite defensive connection configuration: https://sqlite.org/c3ref/c_dbconfig_defensive.html
- SQLite trusted schema: https://sqlite.org/pragma.html#pragma_trusted_schema
- SQLite TEMP triggers on non-TEMP tables: https://sqlite.org/lang_createtrigger.html#temp_triggers_on_non_temp_tables

These observations justify a fail-closed SQLite profile and exact writer
serialization. They do not prove the host filesystem, storage controller, or
power-loss stack honors every durability primitive.

## OpenSSL context ownership

- `SSL_CTX_up_ref`: https://docs.openssl.org/3.5/man3/SSL_CTX_up_ref/
- `SSL_CTX_free`: https://docs.openssl.org/3.5/man3/SSL_CTX_free/
- OpenSSL thread safety: https://docs.openssl.org/3.5/man7/openssl-threads/

Reference retention closes the raw `SSL_CTX*` lifetime race. It does not make
concurrent mutation of one shared context safe; the caller must continue to
serialize configuration mutation.

## Rollback protection model

- The Update Framework specification: https://theupdateframework.github.io/specification/latest/

TUF's rollback defenses depend on trusted version state retained separately
from newly fetched metadata. Rev0891 follows the same separation conceptually:
the database carries a hash chain, while an optional exact generation/digest
anchor must be retained outside that database to detect whole-file rollback.
AnonSync does not yet implement the external anchor store or signed membership
metadata.

## Design inference

A hash chain inside the same replaceable SQLite file is integrity evidence, not
self-sufficient rollback protection. A durable external monotonic anchor, clear
crash ordering between database and anchor, signed update provenance, and
recovery semantics are the next load-bearing membership steps.
