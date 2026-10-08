# AnonSync rev0816 revision notes

## Mission-level result

Rev0816 closes an evidence-classification error at the SQLite transaction owner
boundary. AnonSync already denied mutation whenever it could not revalidate the
exact connection, transaction, savepoint, callback, process, thread, and mutex
capability generation. The remaining error was what happened *after* that
denial: a temporary allocator failure while probing authority was treated as
positive proof that the exact generation had been replaced, so the RAII guard
permanently discarded authority over a transaction or savepoint that could still
be live.

The corrected rule is stricter and more precise:

> Failure to prove authority denies the current use. Permanent revocation,
> however, requires evidence that the generation ended or was superseded.

This preserves fail-closed mutation without converting temporary absence of
evidence into false evidence of replacement.

## Exact lineage

The sole source parent is
`AnonSync-rev0815-2026.07.17.07.06-cutpointmodel-closeplan-retryproof-allocfence.zip`
with SHA-256
`af654d747a7a02f6aa92d1ed1895d8921433e3bb23b40cb467d4004b7a0ca34a`.
The exact parent ZIP passes 25/25 package checks and its canonical extracted
`AnonSync/` root passes 21/21. No build tree, reconstructed approximation, or
unsealed intermediate was used as source.

## Reproduced parent defect

The rev0816 allocator worker was compiled against production owners copied
byte-for-byte from the sealed rev0815 parent. The same current harness then
reproduced three deterministic failures at allocator cut 1:

- sticky failure during savepoint release permanently revoked a still-live mark;
- one-shot failure during savepoint rollback permanently revoked a still-live
  mark; and
- sticky failure during transaction commit permanently revoked a still-live
  transaction.

The harness and scenarios are identical when compiled against rev0816. All three
recover by exact revalidation and retry. The differential, source hashes, worker
outputs, and build log are retained under
`REVISION_EVIDENCE/rev0816/defect_reproduction/`.

## Production correction

Use-time boundary authority is now classified as one of three states:

- `Current`: the exact AnonSync authorizer bridge was observed and the ownership
  probe completed successfully;
- `Invalid`: process, thread, mutex capability, connection generation,
  transaction generation, savepoint generation, or authorizer ownership is
  positively known to have ended or changed; or
- `Indeterminate`: a transient/resource failure prevented the probe from
  completing, so the current use is denied but the generation is retained for
  a later exact retry.

The public boolean compatibility checks still grant only `Current`; neither
`Invalid` nor `Indeterminate` authorizes work. Transaction and savepoint guards
now revoke permanently only on `Invalid`. `Indeterminate` throws a retry-required
failure while preserving the exact proof object.

After a failed transaction-stack effect, the owner still observes
`sqlite3_get_autocommit()`. SQLite documents that resource failures can
implicitly roll back the outer transaction. When autocommit proves that the
outer transaction actually ended, both transaction and savepoint authority are
revoked immediately. Thus rev0816 does not preserve a generation after genuine
automatic rollback.

## Exhaustive SQLite allocation-cut campaign

A new 880-line Linux worker installs a SQLite allocator overlay using
`SQLITE_CONFIG_GETMALLOC` and `SQLITE_CONFIG_MALLOC` before initialization. Each
scenario first measures its no-fault allocation frontier, then executes every
reachable cut in two modes:

- one-shot: reject exactly the selected allocation; and
- persistent: reject the selected allocation and every later allocation.

Every cut runs in a fresh `fork`/`exec` process. All C++ strings needed by the
child launch path are prepared before `fork`; the child performs only descriptor
operations, `exec`, and `_Exit`. The overlay accounts for live blocks and bytes
through malloc, realloc, and free, and every worker proves that its count returns
to zero after handles are closed and SQLite is shut down. `sqlite3_shutdown()` is
not represented as a leak detector.

The six reviewed frontiers are:

| Boundary | Baseline SQLite allocations |
|---|---:|
| transaction begin | 15 |
| savepoint begin | 28 |
| savepoint release | 28 |
| savepoint rollback | 29 |
| transaction commit | 28 |
| transaction rollback | 28 |

The 156 baseline allocation positions yield 312 injected cuts per campaign.
Including the six no-fault baselines, one campaign executes 318 isolated
processes, 642 parent-side recovery assertions, and 2,320 worker-side checks.
Ten unsanitized campaigns pass: 3,180 processes, 3,120 injected cuts, 6,420
parent assertions, and 23,200 worker checks.

## Audit and refactor result

The reviewed runtime helpers no longer request the optional fifth-argument error
buffer from `sqlite3_exec()`. That buffer is allocated by SQLite and imposes a
manual `sqlite3_free()` obligation after the primary operation. The transaction
owner, generic SQLite support, runtime connection profile, replay-ledger
rollback paths, and runner rollback paths now use the connection-owned
`sqlite3_errmsg()` evidence instead. This removes redundant post-effect OOM
cutpoints and manual error-buffer ownership from the reviewed production paths.
Test-only hostile fixtures that intentionally exercise the raw API remain
explicitly inventoried.

Four deterministic source audits now form the proof perimeter:

- allocator-fault ownership and campaign audit: 98/98;
- broad transaction-stack authority audit: 98/98;
- exception-composition audit: 52/52; and
- replay-ledger schema/transaction contract audit: 29/29.

The allocator audit binds the tri-state owner, retry-preserving guard behavior,
automatic-rollback revocation, process-isolated campaign, exact frontiers,
allocator accounting, CMake/CTest/sanitizer registration, runtime error-buffer
inventory, and package-verifier inclusion.

## Source delta and repository shape

Fifteen active files changed: 1,814 inserted and 131 removed lines. No bundled
third-party file changed. The active implementation projection contains 158
files and 15,682,202 bytes with SHA-256
`eeb83f374abb3ca7f2bc546cb52126aef18906cc91851787d6d7673d33bc613a`.

The largest new file is the 31,466-byte allocation-cut worker. Production changes
are concentrated in the SQLite connection-authority owner, transaction/savepoint
RAII owner, and removal of optional `sqlite3_exec()` error-buffer ownership.
`sync_domain.cpp` remains the principal local compilation bottleneck at 15,371
lines and is not represented as solved by this revision.

## Validation

- An initially empty Ninja Debug tree built every target with GCC 14.2.0 and
  C++20. Command-window interruptions required resuming the same immutable tree;
  no single uninterrupted timing claim is made. A final invocation reported
  `ninja: no work to do.`
- The complete final CTest invocation passes 92/92 in 28.42 seconds, including
  the existing crash corpus and the new 318-process campaign.
- Ten additional normal allocator campaigns pass, totaling 3,180 workers and
  3,120 injected cuts.
- A focused GCC ASan/UBSan lane completes five allocator campaigns, ten
  connection-authority repetitions, and ten exception-composition repetitions.
  Changed C++ is instrumented; bundled `sqlite3.c` is deliberately
  uninstrumented; LeakSanitizer and a full-project sanitizer claim are excluded.
- A focused Clang 17 Release build passes one complete allocator campaign plus
  ten owner and ten exception-composition repetitions with no compiler warnings.
  This is not represented as a full-project Release gate.
- The canonical release directory passes 21/21 package checks and the sealed ZIP
  passes 25/25, including exact manifest inventory, active-projection
  recomputation, safe archive paths, one canonical root, and ZIP CRC integrity.

## Research basis

The campaign follows SQLite's documented OOM-testing pattern: replace the
allocator before initialization, advance the failure index through the complete
operation frontier, and test both one-shot and persistent failure. SQLite also
documents the ownership of `sqlite3_exec()` error strings, automatic outer
rollback on selected failures, and authorizer replacement/prepare-time callback
semantics. Exact official references and their design consequences are retained
in `REVISION_EVIDENCE/rev0816/RESEARCH.md`.

## Remaining boundaries

This revision does not exhaust arbitrary C++ global-`new` failures. The next
local allocator experiment should inject at guard construction, close-plan
construction, exception composition, and caller catch/retry boundaries without
interfering with the process harness itself.

The larger reliability gap remains a VFS and process-crash oracle spanning
SQLite journal/WAL operations and AnonSync's sidecars, manifests, staging files,
renames, directory synchronization, and externally visible publication. Beyond
local durability, the project still lacks an executable distributed convergence
algebra, disposable hostile-database interpretation, and a complete payload
confidentiality, metadata-leakage, device enrollment, key rotation, revocation,
recovery, forward-secrecy, and post-compromise-recovery design.
