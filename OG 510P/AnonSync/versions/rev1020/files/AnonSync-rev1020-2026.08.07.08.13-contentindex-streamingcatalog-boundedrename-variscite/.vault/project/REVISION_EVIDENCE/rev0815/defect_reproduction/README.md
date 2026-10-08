# Exact-parent allocation-window reproduction

`parent-allocation-window-reproduction.json` scans the exact verified rev0814
production owner and records the source shape around fenced savepoint rollback.
It binds the parent source digest and demonstrates that release SQL, the release
diagnostic label, and a copied callback-permit name were constructed after the
rollback branch.

This is evidence of a latent exception-composition window. It is not a runtime
claim that an allocator failure, corruption, or data-loss incident was observed.
Rev0815 removes the unnecessary application allocation interval and separately
models SQLite-denied release after successful rewind as an intentional retryable
partial state.
