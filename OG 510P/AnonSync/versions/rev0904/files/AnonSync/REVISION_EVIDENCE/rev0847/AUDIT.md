# AnonSync rev0847 deep audit

## Executive finding

The strongest local invariant in AnonSync is that observations do not become
authority merely because a subsystem accepted or serialized them. The deep audit
found one direct violation of that principle in `SqliteVerificationBudget`:
SQLite retained the owner's raw address as progress-handler context, while the
owner bound only process incarnation and allowed sequential use from a different
thread.

That was not merely missing documentation. It was an executable authority gap
across callback entry, ordinary counter mutation, handler detachment, and
object destruction. Rev0847 closes the gap with exact process+thread capability
checks and direct fail-stop proofs.

## Boundary reconstructed

`SqliteVerificationBudget` performs four coupled roles:

1. owns row, byte, and virtual-machine-step budgets and counters;
2. installs one `sqlite3_progress_handler` on a database connection;
3. passes its own address as the callback's opaque context;
4. detaches the handler during explicit detach or destruction.

Those roles create a raw lifetime edge from SQLite into C++. SQLite serialized
mode can serialize calls through the connection, but the callback pointer still
names one application object with ordinary fields. The pre-revision process-only
check could not distinguish the creating thread from a later thread in the same
process.

## Corrected invariant

The owner now freezes, in field and construction order:

1. `SyncProcessIncarnation process_id_`;
2. `SyncThreadIncarnation thread_id_`;
3. database and remaining mutable state.

Every guarded path checks process before thread. Throwing operations call
`require_current_execution_or_throw()` before reading the private `label_` or
any mutable budget state. Unauthorized errors use the fixed public boundary name
“SQLite verification budget,” preventing diagnostic-label disclosure.

The callback, `noexcept` accessors, detach, and destructor call
`require_current_execution_noexcept()`. Invalid tokens and mismatched tokens
both fail stopped through the reviewed process-capability violation exit path.
No unauthorized `noexcept` path falls through to SQLite or the owner fields.

## Runtime proof

The 70-check focused corpus covers ordinary budget behavior and the new
authority cases. In particular:

- a foreign-thread throwing `consume_row()` call is rejected;
- the rejection does not contain the caller's private diagnostic label;
- row, byte, and step counters remain unchanged;
- the originating thread remains authorized after rejection;
- foreign-thread SQLite progress callback entry exits 86;
- foreign-thread progress-handler detach exits 86; and
- foreign-thread destruction exits 86.

The three fail-stop cases execute in inherited child processes so the parent can
verify exact exit semantics without ending the test runner.

The focused corpus passes 100 consecutive executions. The four affected
ownership/process executables pass 128/128 checks under Clang 17 `-Werror` and
under GCC 14 ASan+UBSan with leak detection.

## Audit refactor

The old budget audit located a function by finding a name and slicing until the
next function-looking marker. That approach was vulnerable to braces or tokens
inside comments, strings, character literals, raw strings, and default `{}`
arguments. Rev0847 replaces it with a small brace-aware lexical extractor that
skips those constructs and identifies the real body delimiter.

The 53-check audit now establishes:

- exactly one production progress-handler owner translation unit;
- the expected registration and disable sites;
- process/thread fields, ordering, and constructor capture;
- process-before-thread checks on throwing and `noexcept` surfaces;
- callback, detach, and destructor coverage;
- rejection before private diagnostics and mutable state;
- direct runtime proof markers for preservation, non-disclosure, and death cases;
- bounded/reporting composition; and
- release-package inclusion of the production owner, focused test, and audit.

## Adjacent audit findings

Adding the death corpus changed the independently discovered inherited-process
inventory from 11 translation units / 20 spawn sites to 12 / 21. Two dedicated
audits and CMake reflected the change, but `audit_self_exec_test_process.py`
still embedded the old count. That stale duplicate caused one audit failure and
was corrected. Final results:

- verification budget: 53/53;
- generic thread incarnation: 33/33;
- SQLite process authority: 87/87;
- raw-fork boundary: 11/11;
- inherited-process ownership: 15/15;
- self-exec process ownership: 36/36;
- registered audit registry: 41/41.

The package verifier also had a proof-surface omission: it required the budget
implementation but not the focused test or architecture audit. Both are now
mandatory, preventing a handoff from retaining production code while silently
dropping its direct proof.

## What remains missing

### Callback-context inventory

The fix proves one owner, not the entire callback universe. Every application
pointer retained by SQLite, OpenSSL, libc, threads, or other C APIs should be
classified by lifetime, thread/process authority, reentrancy, detach ordering,
exception policy, and synchronization. A generated inventory would be less
fragile than multiplying hand-maintained audit counts.

### Convergence semantics

The cube still lacks an executable operation algebra and deterministic reference
model for duplicate, reordered, concurrent, partitioned, retried, and restarted
histories. Local authority and crash recovery are necessary but not sufficient
for distributed convergence.

### Privacy/device/key protocol

Authentication, signatures, and ledger integrity do not establish anonymity.
Payload encryption, device membership, key epochs, revocation, state-loss
recovery, forward secrecy, post-compromise recovery, metadata leakage, backup
custody, rollback resistance, and erasure limits remain unspecified or
unproved.

### Hostile-input isolation

Hostile SQLite and document interpretation still occurs in the principal
process. Resource budgets reduce work but do not provide a process boundary.
Disposable workers with bounded descriptor protocols and layered OS isolation
remain a high-value architectural step.

### Cross-resource crash oracle

SQLite transactions/WAL/checkpoints, atomic files, directories, JSONL journals,
receipts, and downstream effects have strong local tests but no single cutpoint
oracle relating all durable prefixes.

## Waste and correction strategy

The current rigor is real but expensive. The 42 source audits, 2,530-line CMake
file, very large domain and selftest translation units, and 25.8 MB historical
evidence corpus amplify every change. The corrective direction is not to remove
proof. It is to replace duplicated lexical proof with smaller typed production
owners, generated inventories, deterministic semantic models, and
content-addressed lineage. Superseded audits should be retired rather than
retained forever in parallel.

## Claims deliberately not made

Rev0847 does not claim that thread affinity synchronizes concurrent access, that
all callback contexts are classified, that ThreadSanitizer passed, that the
whole project was sanitized, that a Release all-target build passed, that
Windows was exercised, or that distributed convergence, anonymity,
confidentiality, hostile-worker isolation, arbitrary power-loss completeness,
or secure erasure is implemented.
