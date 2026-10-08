# Rev0814 audit

## Mission result

Rev0814 makes nested SQLite rollback scope an evidence-bearing C++ capability
rather than ambient SQL text. The immediate security defect was not a failed
DELETE or failed comparison; it was a compound transition whose destructive
prefix could survive after a later authority check failed and the caller caught
the exception.

## Corrected defect

Checkpoint-root reset is authorized as one transition: delete the root, accept
its reviewed cascades, prove and update sticky owner-mode evidence, then consume
the single-use permit. Rev0812 executed those steps directly in the caller's
outer transaction. A stale post-permit mode row caused the final compare-and-swap
to fail, but a caller could catch that exception and commit the already executed
root deletion.

The exact parent plus only the new regression test fails 44/45. Rev0814 creates a
fenced `SyncSqliteSavepoint` from the permit's exact transaction authority before
the DELETE. Any late failure rewinds and releases that mark; unrelated earlier
outer-transaction work remains available to commit.

## Typed savepoint owner

The new noncopyable/nonmovable owner binds:

- SQLite handle and serialized connection mutex;
- process ID and process salt;
- connection incarnation and authorizer generation;
- exact outer typed transaction generation;
- monotonically allocated savepoint generation;
- owner-thread incarnation and retained close-fence capability; and
- an internally generated injection-proof name.

All potentially throwing C++ allocations complete before SQLite accepts the
mark. The bridge records the frame before issuing SQL and removes it if begin
fails. Fenced marks close only in reverse construction order. Rollback is
`ROLLBACK TO` plus `RELEASE`; outer commit refuses any live typed mark; outer
rollback clears the complete modeled stack. Callback replacement, stale
transaction authority, foreign-thread mutation, inherited-fork destruction, and
live-handle close all fail closed.

An explicit compatibility constructor remains for handles with no AnonSync
authority. It uses process-unique generated names and observation-based
semantics; it is not represented as an exact authority proof.

## Refactor

Two ad hoc schema savepoint implementations now consume the shared owner:

- checkpoint-owner schema migration; and
- peer-ingress payload-store schema migration.

Production savepoint SQL is centralized in
`src/sync_sqlite_connection_authority.cpp`. The final audit inventories nine raw
savepoint-stack literals, all in that one invariant owner, and zero elsewhere.
Legacy raw `BEGIN`/`COMMIT`/`ROLLBACK` sites remain separately inventoried as
future migration candidates rather than being mislabeled safe.

## Audit integration findings

The first complete 88-test integration attempt failed two old source audits.
They encoded the pre-refactor destructor shape and expected reset to expose a raw
destructive prefix. The resolution was not to delete the objections: the process
audit was strengthened to require inherited-fork live-savepoint behavior, and
the owner audit was strengthened to require exact nested rollback ownership and
ordering.

Final structural gates:

- SQLite transaction-stack authority: 78/78;
- SQLite process/fork authority: 87/87;
- checkpoint-owner fence: 51/51; and
- production raw savepoint-stack SQL outside the owner: 0.

## Behavioral proof

- fresh empty-tree Debug all-target build: passed;
- fresh complete CTest: 88/88;
- connection authority/savepoint corpus: 133/133;
- process/fork authority corpus: 44/44;
- checkpoint owner recipient/reset corpus: 45/45;
- checkpoint owner schema corpus: 31/31;
- runtime/payload-store corpus: 46 checks;
- 12 repeated combined iterations: 3,588 checks; and
- focused C++ ASan/UBSan, three iterations: 531 checks.

The sanitizer lane instruments the C++ SQLite authority, transaction/savepoint,
and fork proof code. Bundled `sqlite3.c` is deliberately uninstrumented and leak
detection/full-application coverage are not claimed.

## Remaining high-risk gaps

The typed savepoint owner does not make SQLite and filesystem publication one
crash-atomic protocol. It does not provide distributed consensus, trusted time,
complete hostile-database process isolation, convergence algebra, payload
confidentiality, metadata hiding, key lifecycle, forward secrecy, or
post-compromise recovery.

The explicitly unfenced compatibility lane cannot prove exact savepoint identity
if external code manipulates the same handle. Continued work should migrate the
remaining legacy raw transaction boundaries and narrow/remove this lane where
production ownership is available.

The next high-value local audit is exception composition: generate traces where
each authority-bearing mutator fails after every internal effect, callers catch
or retry, and outer transactions commit or roll back. That should become a
small independent transition model rather than a growing set of hand-selected
examples.
