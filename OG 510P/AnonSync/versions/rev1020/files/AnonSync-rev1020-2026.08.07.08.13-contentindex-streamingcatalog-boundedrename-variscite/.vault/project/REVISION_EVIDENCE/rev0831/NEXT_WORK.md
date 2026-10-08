# Next high-leverage work after rev0831

1. **Extract and migrate the `sqlite_replay_ledger.cpp` selftest tail.** Five
   raw-fork children run lock-holder or restore C++ from a production-linked
   translation unit. Move the corpus to the selftest library, add versioned
   self-exec helper modes, and prove the ordinary runtime graph no longer
   compiles those fixtures.
2. **Migrate payload-store and atomic-publication crash processes.** These
   children create their SQLite/publication state after fork and gain no valid
   authority from inherited C++ memory. Reuse the process owner and bind every
   payload digest, path identity, contender ID, and cutpoint after exec.
3. **Replace the allocator worker shim.** Convert its fork/dup2/exec sequence to
   `posix_spawn` file actions with explicit stdout/stderr capture, bounded reads,
   and the same move-only owner.
4. **Split mixed fork semantics.** Keep raw fork only where inherited authority
   is the subject of the test. Move isolation-only race tests to self-exec and
   audit the remaining child branch against a minimal permitted-operation list.
5. **Build the SQLite VFS crash-cut oracle.** Enumerate write, sync, truncate,
   delete, lock, journal, WAL, and shared-memory frontiers, then join recovered
   database state to receipt-publication state and typed recovery authority.
6. **Model process ownership independently.** Generate traces over spawn,
   transfer, timeout, leader exit, descendant creation, wait errors, and parent
   destruction; differentially compare the small model with the C++ owner.
7. **Disposable hostile-database worker.** Add resource limits, no-new-
   privileges, seccomp, and Landlock around one-request inspection, returning a
   small typed result rather than a live SQLite capability.
