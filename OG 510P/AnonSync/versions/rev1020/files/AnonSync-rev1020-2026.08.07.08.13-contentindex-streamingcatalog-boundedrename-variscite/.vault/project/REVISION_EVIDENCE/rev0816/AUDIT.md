# Rev0816 audit

## Audit question

Can an allocation failure in SQLite's use-time transaction ownership probe be distinguished from positive evidence that the callback, connection generation, transaction generation, or savepoint generation has actually been replaced or ended?

Rev0815 answered that question with one boolean. A failed probe returned false, and RAII catch paths permanently revoked the guard. Under `SQLITE_NOMEM`, the probe can fail before the authorizer callback runs. Absence of that callback observation is then absence of evidence, not evidence of replacement. The exact transaction or savepoint can remain live and retryable.

## Reproduced parent defect

The current rev0816 allocator worker was compiled against unchanged rev0815 production owners. Three deterministic cut-1 traces fail in the parent: savepoint release, savepoint rollback, and transaction commit. Each failure says a still-live exact generation was permanently revoked. The same binary source compiled against rev0816 passes all three and completes recovery.

This is a runtime parent/current differential, not a speculative source-shape finding.

## Production correction

Use-time ownership now has three states:

- `Current`: the exact AnonSync authorizer bridge was observed and prepare/finalize completed.
- `Invalid`: exact identity is known to have ended, been superseded, or been replaced.
- `Indeterminate`: the probe could not complete, so this use is denied but the generation is retained for retry.

Mutation remains fail-closed. No operation proceeds under `Indeterminate`. Only `Invalid` permanently revokes. SQLite autocommit is still observed after a failing boundary because SQLite can automatically roll back the outer transaction on resource errors; that observation revokes both levels when the transaction actually ended.

## Allocation-cut oracle

The new Linux/bundled-SQLite worker installs an allocator overlay through `SQLITE_CONFIG_GETMALLOC` and `SQLITE_CONFIG_MALLOC` before SQLite initialization. Every no-fault allocation frontier is walked in two modes: one rejected allocation and persistent failure from the selected allocation onward. Each cut executes in a fresh process.

Six boundaries produce 156 baseline allocations and therefore 312 injected cuts per campaign. One campaign uses 318 processes, performs 642 parent checks, and performs 2,320 checks inside workers. Ten unsanitized campaigns pass: 3,180 processes, 3,120 injected cuts, 6,420 parent checks, and 23,200 worker checks.

The overlay tracks live blocks and bytes through malloc, realloc, and free. Every worker closes all handles, shuts SQLite down, and proves the overlay count returns to zero. `sqlite3_shutdown()` itself is not misrepresented as a leak detector.

## Refactor result

Reviewed runtime helpers no longer request `sqlite3_exec()`'s optional allocator-owned error string. They use the connection-owned `sqlite3_errmsg()` evidence instead. This removes redundant post-effect OOM cutpoints and manual `sqlite3_free()` ownership from transaction boundaries, generic support, runtime profile setup, replay-ledger rollback paths, and runner rollback paths. Test-only hostile fixtures remain explicitly inventoried rather than being conflated with runtime code.

## Structural and compiler gates

The final source passes 98/98 allocator-fault checks, 98/98 broad transaction-stack checks, 52/52 exception-composition checks, and 29/29 schema-contract checks. A fresh Debug all-target tree reaches dependency closure and passes 92/92 CTest cases. A focused Clang 17 Release build passes the complete campaign plus ten owner and ten composition repetitions.

A focused GCC ASan/UBSan lane completes five allocator campaigns, ten owner repetitions, and ten composition repetitions. Changed C++ is instrumented; bundled `sqlite3.c` is not; LeakSanitizer and a full-project sanitizer claim are deliberately excluded.

## Remaining boundaries

The next allocator layer is C++ global-new failure at guard construction and diagnostic composition. The larger reliability gap remains VFS I/O and crash cuts spanning SQLite, sidecars, manifests, staging files, renames, and directory sync. Beyond local durability, AnonSync still needs an executable distributed convergence algebra, disposable hostile-database interpretation, and a complete confidentiality/anonymity/key-lifecycle protocol.
