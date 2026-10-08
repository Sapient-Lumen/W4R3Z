# Rev0983 research notes

SQLite's online backup API copies one logical database through SQLite's transaction machinery; it does not make a raw main/WAL/SHM inode family interchangeable. Rev0983 therefore restores logical contents through the retained writable VFS, preserves the displaced logical state as a separately verified artifact, and treats recovery lineage advancement plus an independent reopen as distinct post-copy proofs.

SQLite documents that a successful terminal backup step completes the backup and may commit the destination transaction. That makes a throwable post-`SQLITE_DONE` observer unsafe: it could report failure after mutation is already durable. The retained hook is limited to nonterminal intervals between page-copy effects.

A future crash-idempotent replacement ceremony still needs a small external durable action receipt, or an equivalently conservative offline rule, distinguishing pre-copy, copied-before-epoch, epoch-advanced, and final-reopen states. Until then, uncertain continuity resets retention-mark age and cannot authorize destructive collection.
