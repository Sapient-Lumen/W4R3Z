# Rev0804 online research and design implications

Research was limited to primary or official sources for implementation claims.

## SQLite destruction callbacks

SQLite documents the `sqlite3_create_function_v2()` destructor as the cleanup
hook for the application-data pointer when the function is deleted, ordinarily
when the database connection closes. That makes it a direct executable oracle
for whether `sqlite3_close()` happened before AnonSync rejected an invalid move
source.

Source: https://www.sqlite.org/appfunc.html

SQLite's binding API likewise gives SQLite ownership of a supplied value through
an application destructor. The destructor is invoked when SQLite no longer
needs the bound value, including statement cleanup. Rev0804 uses that behavior
to prove whether `sqlite3_finalize()` ran before source validation.

Source: https://sqlite.org/c3ref/bind_blob.html

Design implication: C++ wrappers must treat close/finalize as arbitrary callback
boundaries, not as inert pointer clearing. Source authority must be validated and
escrowed first, and the exact destination generation needs an in-progress fence
until SQLite returns.

## SQLite and fork

SQLite's corruption guidance warns against carrying an open SQLite connection
across `fork()` and specifically warns that the child should not close an
inherited connection. Rev0804 applies the same ownership principle to C++
wrappers: a copied child object is representation, not child authority, and its
invalid use must not cause child-local or parent-relevant cleanup first.

Source: https://sqlite.org/howtocorrupt.html

## Crash and VFS testing

SQLite's own testing documentation describes specialized VFS layers that inject
I/O errors and simulate crash interruption, reordered writes, and corruption,
followed by recovery checks. AnonSync needs the same mechanism plus a separate
domain-state oracle; SQLite structural integrity alone cannot decide whether a
recovered receipt/checkpoint/workorder state is protocol-permitted.

Source: https://sqlite.org/testing.html

## Convergence research

The CRDT literature states the algebraic/causal conditions under which replicas
can converge without coordination. Those conditions should be made explicit for
AnonSync operations rather than inferred from the presence of tombstones,
idempotency keys, or conflict copies.

Primary paper: https://hal.science/hal-00932836/file/CRDTs_SSS-2011.pdf

Speculation: a small executable reference model could classify each operation as
commutative/order-sensitive, idempotent/single-application,
monotone/retracting, and causally dependent/independent. Production C++ traces
could then be checked under duplication, omission, reordering, partitions,
restart, and key-epoch changes.

## Key lifecycle and privacy

RFC 9420 (Messaging Layer Security) formalizes group epochs, forward secrecy,
and post-compromise security properties. It is relevant design research for
AnonSync device/key epochs, but does not establish that AnonSync currently has
those properties and is not necessarily the correct protocol for its topology.

Source: https://www.rfc-editor.org/rfc/rfc9420

Design implication: the project should first publish an adversary and leakage
model—payload, filename/path, size, timing, topology, equality, access patterns,
and server visibility—then choose key agreement, rotation, revocation, recovery,
and memory-erasure mechanisms that satisfy that model.
