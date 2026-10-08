# AnonSync rev0814 revision notes

## Mission-level result

Rev0814 makes nested rollback scope an evidence-authorized transition boundary.
A savepoint is no longer ambient SQL that happens to succeed: the owner proves
the exact process, connection, callback generation, outer transaction, inner
mark, thread, lifetime, operation, and name before allowing a stack transition.

This repairs a concrete compound-transition defect. A checkpoint reset could
delete the root and cascade owner state, fail a later sticky-evidence
compare-and-swap, then have the caller catch the exception and commit the
destructive prefix. Rev0814 ensures the permit-authorized reset either completes
as one nested unit or leaves the root and cascaded owner intact.

## Parent and lineage

The exact parent is `AnonSync-rev0812-2026.07.17.04.13-schemaattest-casefold-migrationseal-constraintprofile.zip` with SHA-256 `566a24efc959383546daf4bd261dc0d51c221059f0a9c1040dcc626e71f459c9`. Its ZIP
passes 25/25 package checks and its extracted canonical root passes 21/21.

No rev0813 archive was published. A prior response named one, but sealing failed
before creation. Rev0814 is a direct child of verified rev0812 and contains the
recovered reset repair plus the shared savepoint owner and stronger audits.

## Defect reproduced against the parent

The new catch-and-commit regression was inserted into the exact parent without
changing production code. It failed 44/45:

`caught late reset failure cannot commit the destructive DELETE prefix`

The negative run and exact test-only patch are retained under
`REVISION_EVIDENCE/rev0814/defect_reproduction/`.

## Production corrections

### Typed `SyncSqliteSavepoint`

The new scope-bound owner is noncopyable, nonmovable, process-bound, thread-affine, and bound to the exact live outer transaction on an authorized handle.
It uses internally generated names, one-shot authorizer permits, monotonic inner
generations, retained recursive connection-mutex/close capabilities, LIFO
closure, rollback-plus-release, and outer-commit refusal while any inner mark is
live.

Every C++ allocation that can fail is completed before SQLite accepts the mark.
A failed begin removes the reserved frame. Alien callback replacement never
causes a raw fallback to operate on an ambiguous later stack.

### Atomic checkpoint reset

`delete_checkpoint_root_with_permit_in_write_transaction_or_throw()` now creates
one fenced savepoint from the reset permit's exact transaction authority before
issuing the DELETE. It releases the mark only after cascade verification and the
sticky-mode exact compare/reload succeed, then consumes the permit. The focused
regression proves a caught late failure preserves root and owner while retaining
unrelated earlier outer-transaction work.

### Shared schema rollback owner

The checkpoint-owner schema migration and peer-ingress payload schema migration
no longer maintain ad hoc raw savepoint wrappers. Both consume the shared typed
owner. Production raw savepoint-stack SQL is now centralized in one reviewed
file.

## Audit result

A new CTest-registered transaction-stack source audit passes 78/78. It inventories
nine raw savepoint-stack literals, all in
`src/sync_sqlite_connection_authority.cpp`, and zero outside it. The process
authority audit passes 87/87 and requires inherited-fork live-savepoint behavior.
The checkpoint-owner audit passes 51/51 and requires exact reset savepoint
binding and ordering.

The first integrated run passed runtime tests but failed two stale audits, 86/88.
Those gates were strengthened for the new ownership shape rather than removed or
weakened. The negative run is retained.

## Source delta

Fourteen active files changed: 1,692 inserted and
228 removed lines. No bundled third-party source
changed. Key final sizes include 1,627 lines in the connection-authority owner,
358 in the transaction/savepoint RAII implementation, and 899 in the checkpoint
owner recipient.

The active implementation projection contains 154
files and 15,578,433 bytes with digest
`c77e72683c68149b564baf85d5594ff14b40c2406e46c76ef601d7b493f66ab4`.

## Final validation

- Fresh empty-tree Debug all-target build with GCC 14.2, C++20, Ninja 1.12.1,
  bundled SQLite 3.53.3, and `-Wall -Wextra -Wpedantic`: passed.
- Fresh complete CTest invocation: 88/88 in 37.25 seconds.
- Connection authority/savepoint corpus: 133/133.
- Process/fork authority corpus: 44/44.
- Checkpoint-owner recipient/reset corpus: 45/45.
- Checkpoint-owner schema corpus: 31/31.
- Runtime/payload-store corpus: 46 checks.
- Twelve repeated combined iterations: 3,588 checks.
- Focused C++ ASan/UBSan: three iterations, 531 checks.

Bundled `sqlite3.c` was not sanitizer-instrumented, leak detection is not
claimed, and no full-program sanitizer claim is made.

## Remaining boundaries

The explicitly unfenced compatibility constructor is observation-based and
cannot prove exact mark identity after arbitrary same-handle external stack
manipulation. Remaining legacy raw outer transaction boundaries should migrate
to typed ownership over time.

SQLite plus filesystem publication is not one crash-atomic protocol. Hostile
database interpretation remains in the long-lived process. Distributed
convergence, trusted time, privacy, payload encryption, metadata leakage, key
rotation, forward secrecy, and post-compromise recovery remain separate unproved
protocols.

The next high-value local step is an independent exception-composition model
that cuts every authority-bearing mutator after each internal effect, catches or
retries the failure, and differentially checks outer commit/rollback results.
