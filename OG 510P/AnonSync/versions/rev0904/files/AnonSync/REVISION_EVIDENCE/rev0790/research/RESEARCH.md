# rev0790 online research and architectural implications

Research was checked against primary or project-authored sources on
2026-07-15. Links are recorded directly so a future reviewer can re-evaluate
claims against changed upstream documentation.

## SQLite result values: the exact contract AnonSync must enforce

SQLite's result-value documentation states that `sqlite3_column_*` routines are
valid only while the most recent `sqlite3_step()` returned `SQLITE_ROW`; calls
outside a current row or with an invalid index are undefined. It also states
that requesting a representation performs automatic conversion, including REAL
to INTEGER and TEXT/BLOB conversions. For TEXT/BLOB, the safe order is pointer
first and byte count second; byte counts exclude terminators; zero-length BLOB
may have a null pointer; and OOM can look like SQL NULL unless the connection
error is checked immediately.

Source: https://sqlite.org/c3ref/column_blob.html

Implication: a generic convenience wrapper that says “give me an int/string” is
not a neutral accessor. It is a promotion boundary. Rev0790 therefore checks row
state and initial storage class before invoking a representation-specific API,
and preserves explicit byte lengths.

SQLite documents a dynamic type system in which the storage class belongs to
the value, not rigidly to its containing column. Column affinity is a preference
and may convert inserted values. A non-STRICT column may store any storage
class; numeric APIs may then convert it again on read.

Source: https://sqlite.org/datatype3.html

Implication: declared schema spelling cannot substitute for read-time evidence.
A verifier of an externally supplied or locally alterable database must check the
actual result storage class at the point where it mints a C++ value.

## STRICT tables help, but do not replace an exact reader

SQLite STRICT tables constrain declared types and reject values that cannot be
losslessly coerced to the declared type. `integrity_check`/`quick_check` also
check column types in STRICT tables. However, STRICT deliberately attempts
lossless coercion, and older/hostile/legacy databases remain possible.

Source: https://sqlite.org/stricttables.html

Recommendation: migrate durable AnonSync schemas toward versioned STRICT tables
or explicit `typeof()`/range constraints where compatibility permits, but keep
exact read-time validation. Schema enforcement protects writes made through the
normal engine; an exact reader protects the trust transition from durable bytes
to application authority.

## Untrusted database resource limits are still underused

SQLite's security guidance recommends reducing connection limits dramatically
for untrusted SQL or database files and suggests defensive mode, untrusted
schema, authorizers, progress handlers/interrupts, and heap ceilings. Its sample
high-security values include `LIMIT_LENGTH=1,000,000` and `LIMIT_COLUMN=100`.
Runtime limits are explicitly intended to let an application give internally
managed databases broad limits and externally controlled databases much smaller
ones.

Sources:

- https://sqlite.org/security.html
- https://sqlite.org/c3ref/limit.html

AnonSync already enables defensive/query-only/trusted-schema protections and
reduces ATTACHED, trigger depth, variable number, and SQL length for the
read-only snapshot verifier. It does not yet reduce `SQLITE_LIMIT_LENGTH` or
`SQLITE_LIMIT_COLUMN`, install a progress budget, or impose a connection heap
ceiling. The new exact reader supports a per-value maximum, but most callers use
zero (unlimited).

Recommendation: define a named, versioned “untrusted snapshot resource profile”
from measured valid snapshots. Bind maximum schema objects, columns, SQL bytes,
cell bytes, rows, total file/page count, VM operations or wall budget, and heap.
Verify each requested limit after setting it. Do not copy SQLite's example values
blindly; derive AnonSync limits from protocol maxima and corpus measurements.

## Crash testing must distinguish SQLite integrity from protocol validity

SQLite's own testing uses specialized VFS layers and crash simulation to inject
I/O errors, reorder/corrupt writes that were not synchronized, terminate at
many write boundaries, reopen in a separate process, and check both integrity
and expected outcomes. WAL introduces a database file, WAL, shared-memory
index, commit records, and checkpoints; it also does not work across hosts on a
network filesystem because its readers share memory.

Sources:

- https://sqlite.org/testing.html
- https://sqlite.org/wal.html
- https://sqlite.org/vfs.html

Recommendation: AnonSync needs its own state oracle above SQLite. A database can
pass `integrity_check` while the protocol has published a sidecar, conflict
copy, receipt, checkpoint, or filesystem rename in an impossible combination.
The oracle should enumerate allowed post-crash states and verify restart
reconstruction across database, WAL/journal, staging paths, sidecars, and final
filesystem state.

## Convergence and local-first claims require an explicit model

The local-first software work frames offline operation, collaboration, longevity,
privacy/security, and user ownership as related goals—not automatic properties
of local storage. CRDT literature defines convergence through explicit
operation/state rules; replicas receiving the same updates must converge under
stated delivery assumptions. Merkle-CRDT work shows that a content-addressed
DAG can combine transport, persistence, deduplication, and logical-clock
structure under weak messaging guarantees.

Sources:

- https://www.inkandswitch.com/essay/local-first/
- https://inria.hal.science/inria-00609399v2/document
- https://arxiv.org/abs/2004.00107
- https://arxiv.org/abs/1707.01747

Implication: AnonSync should not infer “CRDT” from the presence of replicas,
lineage, hashes, or conflict copies. It needs an executable reference model that
classifies each operation as commutative/order-sensitive, idempotent/single-use,
monotone/retracting, causally dependent/independent, and locally decidable or
coordination-requiring. Generated duplicate, omission, reorder, partition,
concurrent edit/delete, restart, and key-epoch traces should compare the C++
implementation to that model.

## Speculation: a typed evidence descriptor layer

The rev0790 boundary centralizes mechanics, but semantics are still distributed
across free-form wrapper calls and labels. A next step could define generated or
constexpr field descriptors containing:

- expected SQLite storage class and nullability;
- maximum bytes/range and semantic validator;
- sensitivity/redaction policy;
- schema/table/column identity and schema epoch;
- whether the value is hash-bound, signature-bound, or merely diagnostic; and
- the capability type minted after validation.

Queries could bind their projection to descriptors, and generated tests could
mutate each field through NULL, wrong storage class, boundary sizes, embedded
NUL, malformed encoding, and overflow. This would turn “correct wrapper chosen
at every call site” into a reviewable schema-level invariant. It should be
introduced incrementally; a large code generator that silently owns policy
would merely move the authority problem.

## Speculation: a content-addressed evidence DAG

A Merkle evidence DAG could unify immutable lineage, idempotency receipts,
partial synchronization, snapshot discovery, and externalized historical
release packs. A hash pointer proves relationship to exact bytes; it does not
prove that bytes are truthful, authorized, fresh, confidential, available, or
non-equivocating. Each evidence node would still need signer/key epoch, policy
version, subject, operation generation, predecessor/precondition set, and
revocation context. The DAG should carry evidence—not mint authority by
existence.
