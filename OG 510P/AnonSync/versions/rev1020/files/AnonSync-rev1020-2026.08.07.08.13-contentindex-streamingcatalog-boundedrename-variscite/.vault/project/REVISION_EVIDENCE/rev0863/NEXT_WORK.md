# Rev0863 next work

1. Inventory every SQLite path by output, VM-step, elapsed, lock-wait, I/O,
   generation, transaction, cleanup, and publication authority. Do not reuse a
   single timeout label for independent dimensions.
2. Add a deterministic callback-script/reference-model oracle covering multiple
   locking events, deadlock-bypass outcomes, commit contention, rollback
   contention, detach, and connection reuse without scheduler timing.
3. Attest query plans and indexes for duplicate-heavy sidecar frontier reads so
   plan shape, row/byte budgets, VM budgets, and lock budgets reinforce one
   another.
4. Extract the checkpoint-sidecar orchestration from `sync_peer_ingestion.cpp`;
   its large reindent-heavy diff shows that typed owners exist but integration
   remains expensive to review.
5. Build the cross-resource crash oracle spanning SQLite transaction state,
   manifests, staged files, directory durability, receipts, and externally
   visible effects.
6. Move hostile database/document interpretation into disposable workers with
   sealed descriptors and independent CPU, memory, output, syscall, filesystem,
   and wall-time controls.
7. Continue product-defining work: executable convergence histories, then a
   concrete encrypted multi-device identity, key-epoch, revocation, recovery,
   and metadata-leakage model.
