# Rev0859 research and speculation

Primary SQLite documentation was reviewed after the local reconstruction audit.
The conclusions below are architectural guidance, not rev0859 implementation
claims.

## Connection limits are useful but coarser than typed authority

SQLite documents `sqlite3_limit()` as a per-connection mechanism intended in
part for databases influenced by untrusted external sources. In particular,
`SQLITE_LIMIT_LENGTH` can lower the maximum string, BLOB, and encoded row size.
SQLite's documented default maximum string/BLOB length is one billion bytes,
which is far broader than AnonSync's 64-byte hashes, 128-byte identifiers, and
4096-byte portable paths.

Sources:

- https://sqlite.org/c3ref/limit.html
- https://sqlite.org/limits.html
- https://sqlite.org/c3ref/c_limit_attached.html

**Speculation:** a dedicated read-only checkpoint connection should acquire a
frozen `SqliteResourceProfile` that lowers applicable connection limits before
schema or row interpretation. This would be a coarse outer fence; the typed
per-field and aggregate budgets must remain because one connection-wide length
limit cannot express different hash, ID, path, count, and total-manifest rules.

## Exact column extraction has lifetime and conversion rules

SQLite documents that column access is valid only while the statement points at
the current `SQLITE_ROW`, that requesting a representation may perform type
conversion, and that conversions can invalidate prior pointers. Its stated
safest sequence for UTF-8 is text conversion followed by byte measurement.
Rev0859's exact-value gateway centralizes this sequence and rejects the wrong
storage class before returning ownership.

Source:

- https://sqlite.org/c3ref/column_blob.html

**Speculation:** the next extraction should return a short-lived borrowed
`ExactSqliteTextView` capability tied to the statement row generation. The
stream decoder could admit the view's size and semantics before creating the
owned string. Advancing, resetting, or finalizing the statement would revoke
that generation. This is stricter than the current bounded-copy gateway, though
the current maximum scalar allocation is already small.

## CPU cancellation is a singleton callback authority

`sqlite3_progress_handler()` can interrupt long `sqlite3_step()` and prepare
work, but SQLite permits only one progress handler per connection and forbids
the callback from modifying that connection.

Source:

- https://sqlite.org/c3ref/progress_handler.html

**Speculation:** row decoding should compose with the existing retained-callback
claim and exact-generation mutex machinery rather than install an ambient
progress callback. A purpose-owned verification budget can combine VM-step,
wall-clock, and row-event ceilings, then revoke the callback before connection
close. The singleton nature is exactly why a convenience setter would be
unsafe.

## A hard heap limit is process-wide, not transition-scoped

SQLite's hard heap limit applies to all database connections in one process;
allocation can fail when reached, and documented configurations can affect
whether the limiter is enforced. It is therefore not a composable per-request
capability.

Source:

- https://sqlite.org/c3ref/hard_heap_limit64.html

**Speculation:** do not use the process-global hard heap limit as the principal
manifest-defense mechanism. It could make unrelated valid transitions fail and
would still not account for C++ container memory outside SQLite. If hostile
checkpoint interpretation moves to a disposable worker, an SQLite hard limit
can become one defense inside a worker that also has an operating-system memory
limit. Typed count/byte authority remains necessary at the worker result
boundary.

## Likely next architecture

A dedicated checkpoint-reader worker or connection would acquire, in order:

1. a frozen database identity and read-only schema attestation;
2. a connection-scoped SQLite limit profile;
3. an exact-generation progress-budget owner;
4. borrowed, row-generation-bound exact scalar views;
5. the rev0859 streamed manifest owner; and
6. a digest-bound frozen reconstruction receipt returned to the principal
   process.

This layers coarse engine limits, query execution limits, typed event budgets,
and semantic identity without treating any one mechanism as a substitute for
the others.
