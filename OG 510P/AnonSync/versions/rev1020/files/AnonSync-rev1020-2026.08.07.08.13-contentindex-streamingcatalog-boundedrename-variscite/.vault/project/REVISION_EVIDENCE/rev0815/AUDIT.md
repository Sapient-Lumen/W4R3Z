# Rev0815 audit

## Audit question

Rev0814 established exact typed savepoint ownership. Rev0815 audits the next
failure mode: can a logically compound transition be split by an exception that
is unrelated to SQLite after its first effect has already occurred?

For savepoint rollback the effects are intentionally separate in SQLite:
`ROLLBACK TO` rewinds database state but keeps the mark; `RELEASE` erases the
mark. A correct C++ owner must represent the partial state, preserve exact retry
authority, block outer commit while the mark lives, and avoid introducing
needless throwing work between those effects.

## Parent source finding

The exact rev0814 parent built the rollback SQL inline, executed it, then built
the release SQL and release diagnostic label inline. Each authorizer permit also
copied the generated savepoint name into connection state. Those allocations
were not necessary for SQLite semantics and could throw after a successful
rewind but before the release attempt.

The parent reproduction is structural rather than probabilistic. It records the
relevant offsets and source digest and labels the issue as a latent allocation
window, not an observed corruption or data-loss event.

## Corrected owner shape

The fenced close path now has one reviewable pre-effect allocation boundary:

1. validate the exact process, thread, connection, callback, outer transaction,
   savepoint generation, LIFO position, and retained lifetime;
2. probe authorizer ownership;
3. construct a `FencedSavepointClosePlan` containing every SQL and diagnostic
   string required for both close effects;
4. execute the permitted `ROLLBACK TO` when rollback was requested;
5. execute the permitted `RELEASE`; and
6. update the modeled stack only after SQLite closure is observed.

The callback permit borrows `proof.savepoint_name` through `std::string_view`
for one synchronous `sqlite3_exec()` call. The serialized connection mutex and
const proof lifetime make the referent stable; permit destruction revokes the
view. There is no copied permit name to allocate between close effects.

SQLite-originated failure at `ROLLBACK TO` or `RELEASE` remains possible and is
not suppressed. The typed guard retains authority only when a use-time
revalidation proves the same exact boundary remains current.

## Executable composition model

`sqlite_transaction_exception_composition_test.cpp` defines an independent
transaction-stack model and compares every modeled state transition with real
SQLite state. The one-shot authorizer policy creates deterministic cutpoints at:

- savepoint begin;
- release before any rewind;
- rollback-to before rewind;
- release after a successful rewind, in two traces;
- outer commit; and
- outer rollback.

The suite checks not merely that an exception is thrown, but also data contents,
modeled marks, SQLite autocommit state, exact retry behavior, nested LIFO
behavior, and refusal to commit across an unreleased mark. It passes 37/37 and
500 repeated iterations pass 18,500/18,500 checks.

This is a policy-boundary composition model. It is not yet an exhaustive C++ or
SQLite Nth-allocation campaign, VFS failure campaign, or process-crash proof.

## Structural gates

The new focused audit passes 43/43 and enforces:

- target, source, link, CTest, and sanitizer registration;
- borrowed permit-name representation and revocation;
- singular owned close-plan construction;
- plan ordering before rollback, release, and modeled-stack mutation;
- absence of inline SQL or diagnostic construction in the fenced close calls;
- the independent model and all seven boundary-cut traces;
- differential SQLite/model checks and outer-commit fencing;
- retry revalidation in the production RAII guards;
- inclusion in the broader stack audit; and
- inclusion of the owner/model/audits in sealed packages.

The broader transaction-stack audit passes 86/86. It continues to verify that
raw savepoint-stack ownership remains centralized and now binds the composition
model and preallocation contract.

## Validation result

The final active source passes a complete 90-test CTest invocation. The focused
owner and model pass 133/133 and 37/37 respectively. The composition model passes
500 repeated iterations. A focused Debug ASan/UBSan lane passes ten repeated
owner/model iterations, totaling 1,700 checks.

The sanitizer statement is deliberately narrow: changed C++ was instrumented;
bundled `sqlite3.c` was reused uninstrumented; leak detection was disabled; and
no full-program sanitizer result is claimed.

## Remaining severe or expensive boundaries

The transaction model still lacks automatic enumeration of C++ allocation
cutpoints. SQLite supports allocator overlays that fail the Nth allocation; a
one-shot startup worker should use that facility and compare results with the
same logical model.

Database correctness still ends at the SQLite boundary. Receipts, snapshots,
sidecars, staging files, renames, and directory durability must be modeled as
one crash-recovery protocol using a faulting VFS and process crash cuts.

`sync_domain.cpp` remains 15,371 lines. Refactoring should continue by invariant
owner and executable trace contract, not arbitrary line-count slicing. The
largest architectural omissions remain convergence algebra, hostile-input
process isolation, and a complete privacy/key-lifecycle protocol.
