# OPFS block-store write budget guard contract audit slice

Revision: rev0096  
Task: `facility:opfs-block-store-write-budget-guard-contract-audit`

This StorageManager.estimate slice audit ties the `writeBudgetGuard` runtime guard, TypeScript surface, shared fake-OPFS harness refactor, release proof, browser proof, manifest rows, impact map, surface inventory, package scripts, and Makefile current routing together.

The audit is intentionally narrow. It checks the contract surface and current-office routing; behavior evidence comes from `opfs:block-store-write-budget-guard-proof` and `browser:opfs-block-store-write-budget-guard-proof`.

Non-claims: audit only; no managed Chromium launch, no storage reservation, no quota/eviction survival proof, no fsync/durability, no crash recovery, no cross-browser behavior, no production-capacity claim.

- rev0190: writeBudgetGuard budgets staged OPFS puts using transient staged+final bytes before mutation; this remains StorageManager.estimate()-based preflight, not a browser quota or eviction/durability claim.
- rev0191: the contract audit now pins reservation telemetry (`storage:opfs-block-write-budget-reserve/release`, active reserved bytes, and release stats) so the guard does not regress to independent stale-estimate checks for concurrent raw-store puts.
