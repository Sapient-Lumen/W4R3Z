# Rematch-world benchmark cleaned worktrees should be audited before the next zip

## Claim

After a rematch-world publication tree has pruned its exit-ready scratch and reconstructible intermediates, the archive should retain one compact post-prune audit receipt proving the durable publication spine still hash-matches and the tree is actually safe to zip.

## Why this matters

- A prune receipt proves what the workflow attempted to delete, but not yet that the remaining durable files still match their expected content.
- A cleaned tree can still drift if a durable object disappears or mutates between prune execution and packaging.
- One deterministic post-prune audit is smaller than another hand-written cleanup note and turns “probably clean” into a machine-checkable release boundary.

## Operational consequence

- Run `scripts/tools/prune_rematch_world_benchmark_transients.py --execute` only after the retention-exit receipt is ready.
- Then run `scripts/tools/audit_rematch_world_benchmark_post_prune_state.py` against the retention-exit receipt and the execute-mode prune receipt.
- Cut the next revision zip only when the audit says `cleaned_tree_ready_for_zip=true`.
- Treat any durable hash mismatch or lingering transient as a packaging blocker rather than a cosmetic cleanup issue.

## Compactness consequence

The post-prune audit receipt is a small proof that the cleaned tree is ready to package, so future sessions can trust the trimmed archive state without retaining the reconstructed patch or scratch sources any longer than necessary.
