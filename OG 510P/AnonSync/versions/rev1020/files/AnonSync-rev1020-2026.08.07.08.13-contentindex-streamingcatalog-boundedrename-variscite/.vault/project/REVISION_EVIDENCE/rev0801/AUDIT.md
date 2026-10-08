# Rev0801 architecture audit — process-bound persistence authority

## Boundary

Input is a process-local SQLite or filesystem capability minted from current
process evidence. Output is either continued use by that exact process
incarnation, a fresh child-local capability minted after `fork()`, or the direct
capability-violation exit before inherited state can be inspected or destroyed.

The audit covers the process token, retained SQLite path guard, sealed snapshot,
hostile-verification budget/progress callback, their move/destructor paths, the
focused link graph, and release-package source completeness.

## Invariants

1. A live process token is nonzero, stable in one process, and not a raw PID.
2. Every ordinary `fork()` edge advances child lineage before normal child code.
3. The parent token cannot be mutated by a child.
4. Siblings differ by PID and descendants differ by generation.
5. Reuse of an ancestor PID after an observed fork chain does not recreate the
   ancestor token.
6. Generation exhaustion poisons state and cannot wrap into valid authority.
7. One lock-free process-global token owner exists in the final link graph.
8. Empty/moved-from C++ objects remain harmless; materialized inherited owners
   fail-stop on access, move, assignment, callback, detach, or destruction.
9. Inherited seal cleanup cannot close the parent's descriptor, unlink its
   staged snapshot, remove its directory, or detach its VFS relationship.
10. Inherited verification-budget execution cannot use or detach the parent's
    callback context.
11. Denial uses `_Exit(86)` without exception unwinding, `terminate`, or
    `atexit` processing.
12. A controlled child can mint and consume fresh child-local path, seal,
    immutable-open, budget, and query authority.
13. Focused process proof does not link the core monolith, SQLite, or OpenSSL.
14. Focused integrated persistence proof does not link the core monolith.
15. A release package must contain the implementation and proof files that own
    these invariants; a tiny self-manifested archive is rejected.

## Corrected failure modes

### Parent staging deletion from a child

The preserved rev0799 executable demonstrates child move-assignment invoking
inherited cleanup, deleting the parent's staged SQLite snapshot, and breaking
later parent verification. Rev0801 exits before cleanup; the parent file remains
present and verifiable.

### Raw PID resurrection

A PID is recyclable. Treating it as an incarnation token can authorize a later
process after PID reuse. Rev0801 adds an observed fork-lineage generation and
proves a descendant using the ancestor PID remains distinct.

### Inherited callback and path authority

The retained path descriptor and SQLite progress-handler context were process
agnostic. They are now stamped and rejected on every public, move, callback,
detach, and destructor boundary.

### Source-less release lineage

The supplied rev0800 ZIP accurately manifested almost nothing. Rev0801 restores
from rev0799, preserves rev0800 as evidence, and strengthens the release
baseline so package self-description cannot substitute for a source tree.

## Refactor assessment

The token owner is four Ninja actions, two first-party translation units, and
382 lines. The integrated process/persistence proof is 14 actions, six
first-party translation units, and 2,268 lines. Neither focused proof links
`anonsync_core_lib`; the pure token proof also avoids SQLite and OpenSSL.

This is a productive extraction: the boundary owns one explicit invariant,
contains no application policy, has pure algebra tests plus process tests, and
is consumed by multiple persistence owners. It reduces reasoning and sanitizer
cost without inventing a second implementation.

## Audit results

Nine registered source/architecture audits passed. The process authority audit
passed **83/83** checks and inventories remaining compatibility debt rather than
silently declaring it absent. The geometry audit passed **20/20**, seal audit
**37/37**, verification-budget audit **45/45**, scalar extraction **30/30**,
schema contract **28/28**, and sender replay **22/22**.

## Residual risks

- 416 raw SQLite pointer declarations, 34 open-output candidates, and 25
  prepare-output candidates remain in the active inventory;
- direct child use or close of a raw inherited `sqlite3*` remains unsafe;
- arbitrary work after a multithreaded `fork()` remains outside the contract;
- `_Fork()`/raw clone bypasses atfork; first lookup catches PID mismatch, but a
  fully unobserved lineage plus ancestor PID reuse is outside this proof;
- POSIX does not generally bless C++ library work in a fork child; the hook is
  deliberately limited to `getpid`, required-lock-free atomic operations, and
  direct fail-stop;
- the pinned VFS is checked, not wrapped with a universal process filter;
- hostile database interpretation remains in-process and incompletely bounded;
- crash consistency, formal convergence, anonymity, confidentiality, metadata
  leakage, and key lifecycle remain separate unproven properties.

## Recommended continuation

Migrate raw connections into one process-bound RAII owner with narrow statement
borrows. Then execute hostile snapshot interpretation in a freshly `exec()`ed,
OS-limited worker and introduce a fault-injecting VFS crash-cut oracle. In
parallel, build an executable convergence reference model and a written privacy
threat/key-lifecycle contract.
