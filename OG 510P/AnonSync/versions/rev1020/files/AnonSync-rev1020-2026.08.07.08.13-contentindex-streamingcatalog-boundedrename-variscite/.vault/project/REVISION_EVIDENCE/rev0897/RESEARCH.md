# AnonSync rev0897 research notes

## SQLite connection acquisition

SQLite's official `sqlite3_open_v2` documentation says that a connection handle
is usually returned even when open fails and should be closed regardless of the
result. It also says `SQLITE_OPEN_READWRITE` may fall back to read-only. Those
contracts directly motivated the unadopted candidate owner and the explicit
`sqlite3_db_readonly(candidate, "main")` proof before strict adoption.

Primary sources observed during this revision:

- https://www.sqlite.org/c3ref/open.html
- https://sqlite.org/download.html
- https://sqlite.org/

## SQLite dependency status

Official SQLite pages reported 3.53.4, dated 2026-07-24, and listed SHA3-256
`628a44cfe82c66aed1ccbbe85a562d2e33ebe64b3288981ed76285612227934e`
for `sqlite-amalgamation-3530400.zip`. The archive bytes were not successfully
acquired and independently verified in this cloudtainer. The release therefore
retains the bundled SQLite 3.53.3 amalgamation whose existing hashes are checked
at CMake configure time. No 3.53.4 migration is claimed.

## Product speculation

The most valuable next product layer is a bounded supervisor, not a broad UI.
It should consume the existing owner-derived status and clock surfaces, require
explicit policy authority before recovery, and make every retry/shutdown step
restartable. Before that loop grows, bootstrap should become a separate
store-set transaction or manifest-driven command so ordinary commands never
implicitly mint half of a paired authority store.

The name “AnonSync” still outruns the implementation's privacy guarantees.
Mutual TLS and exact SPKI membership authenticate peers and protect content in
transit, but do not hide endpoints, timing, graph shape, overlap, or access
patterns. Mechanisms should follow an explicit adversary and leakage model.
