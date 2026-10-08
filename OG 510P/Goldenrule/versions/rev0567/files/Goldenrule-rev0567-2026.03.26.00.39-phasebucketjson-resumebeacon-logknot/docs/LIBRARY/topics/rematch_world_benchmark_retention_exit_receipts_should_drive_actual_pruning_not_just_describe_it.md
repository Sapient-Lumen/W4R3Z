# Rematch-world retention-exit receipts should drive actual pruning, not just describe it

## Claim

Once a rematch-world publication passes provenance, preflight, bundle, spine-audit, and retention-exit checks, the archive should use one explicit prune step to remove exit-ready scratch and reconstructible intermediates instead of keeping those files by inertia.

## Why this matters

- The archive already distinguishes durable publication objects from exitable transient objects.
- Without an execution step, that distinction still depends on human memory, which is exactly how small scratch residues accumulate across sessions.
- A prune receipt converts “this may leave” into a reproducible cleanup act that can be cited in the handoff log without retaining the deleted files.

## Operational consequence

- Keep the durable publication set retained.
- Run `scripts/tools/prune_rematch_world_benchmark_transients.py` in dry-run mode against the retention-exit receipt to confirm the exact files and bytes covered.
- Rerun with `--execute` only when the exit receipt says the workflow is fully ready.
- Refresh the archive size profile after pruning so the next revision zip reflects the cleaned retained tree rather than the pre-prune workspace.

## Compactness consequence

The prune receipt is smaller than retaining another sidecar family and lets the archive keep only the durable publication spine plus a terse record of what was safe to remove.
