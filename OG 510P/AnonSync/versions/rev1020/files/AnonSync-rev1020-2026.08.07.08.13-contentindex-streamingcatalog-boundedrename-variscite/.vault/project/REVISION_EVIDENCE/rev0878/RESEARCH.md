# rev0878 primary-source research

- SQLite transaction semantics: https://sqlite.org/lang_transaction.html
  `BEGIN IMMEDIATE` starts the write transaction immediately and can report
  `SQLITE_BUSY` when another writer is active. This supports one local causal
  serialization point, not atomicity with another database or filesystem.
- SQLite isolation: https://sqlite.org/isolation.html
  SQLite serializes writers; the rev0878 independent-connection test exercises
  the exact guard boundary used by the implementation.
- Linux `fsync(2)`: https://man7.org/linux/man-pages/man2/fsync.2.html
  File synchronization alone does not necessarily persist the containing
  directory entry, so effect-terminal proof includes directory durability.
- Linux `openat2(2)`: https://man7.org/linux/man-pages/man2/openat2.2.html
  Descriptor-relative resolution constraints are relevant to the next root
  capability refactor; path text alone is not stable directory authority.
- RFC 9266 channel bindings for TLS 1.3: https://www.rfc-editor.org/rfc/rfc9266.html
  The inherited rev0877 transport uses exporter-derived live channel authority.

Inference: the next filesystem milestone should retain or re-attest one exact root
directory object and perform component-relative resolution under that authority.
That reduces root-rebind exposure but still requires explicit restart identity and
platform-specific durability semantics.
