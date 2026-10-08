# Rev0861 research notes

Primary SQLite documentation reviewed during the audit:

1. **Isolation and WAL snapshot behavior** — a read transaction continues to
   see the historical snapshot that existed when it began, even while another
   connection commits newer WAL content. This is the semantic basis for the
   writer-concurrency regression and the one-transaction correction.
   https://sqlite.org/isolation.html

2. **Deferred transaction start** — `BEGIN DEFERRED` records intent but does not
   establish a read snapshot until the first database access. The claimed-path
   query is therefore deliberately the first `SELECT`; all later evidence reads
   use the same transaction authority.
   https://sqlite.org/lang_transaction.html

3. **Collation precedence** — an explicit postfix `COLLATE` operator takes
   precedence over a column's declared collation. Explicit `COLLATE BINARY` is
   therefore required when persisted schema text is not allowed to redefine
   principal or object identity.
   https://www.sqlite.org/datatype3.html

## Speculation

The cube is converging on a useful abstraction: a *durable value capability*.
Such a capability would own one exact database generation and transaction,
explicit schema namespace, byte-exact identity policy, expected schema and
index digest, maximum VM steps, rows, scalar bytes, aggregate bytes, and wall
time, plus one frozen output shape and one post-commit publication operation.

That abstraction could replace both ad hoc read loops and narrative assumptions
about “the current database.” It would also form a narrow protocol for a future
disposable persistence worker: the parent supplies sealed descriptors and a
frozen query capability, while the worker returns only a bounded value plus
resource and snapshot evidence.

The larger mission remains more ambitious than local recovery integrity. A
single-snapshot value prevents impossible local evidence, but convergence still
requires an executable operation algebra and generated multi-peer histories;
“Anon” still requires a defined encryption, membership, key-epoch, revocation,
recovery, and metadata-leakage system.
