# The Rematch Proxy Already Tells Us How to Shrink Search

The archive now has a second implementor-facing result from the leave/rematch proxy:

> In the current proxy opponent pool, `243` raw deterministic `memory_one_exit` codes collapse to only `63` support-distinct decision families.

That is not just a cleanup detail. It changes how the next tranche should search.

## What the new snapshot says

The report in `artifacts/reports/rematch_proxy_canonicalization_snapshot_20260306.{md,json}` performs a structural reachability check over the current focal rematch proxy.
It asks a narrow question:

- which decision parameters of a deterministic `memory_one_exit` policy can ever be consulted,
- before exit,
- against the current proxy pool (`extortion_chi3_v1` and `mem1_generous_tft_v1`)?

Under that exact pool:

1. **Most raw codes are aliases.** `243` raw codes reduce to `63` support-distinct families.
2. **Some collapses are large.** `E****` alone covers `81` raw codes, because once the first move is Exit nothing later matters.
3. **The handoff baseline is genuinely a family.** `CCEEE` is only one readable representative of the `CCE**` family; the other eight members are search aliases in the current proxy.

## Why this matters

The archive already learned that rematching changes the ranking of candidate policies.
This new result adds a second lesson:

- rematching changes **search geometry** too.

If the next implementor optimizes raw `memory_one_exit` genotypes in a rematch-enabled world without canonicalization, the optimizer will spend real budget rediscovering the same behavior under different dead parameters.

That is bad for three reasons:

1. it exaggerates apparent discovery progress,
2. it wastes evaluation budget,
3. and it makes result summaries noisier than they need to be.

## What is pool-specific

This collapse is **not** a theorem about all future partner-choice worlds.
It depends on the current proxy pool.
In particular, both current proxy opponents begin with cooperation, so some suspicious-start states are never reached.

That means the exact quotient can change once the archive adds:

- suspicious starters,
- noisy observation,
- endogenous assortment,
- or richer partner types.

But that does **not** weaken the immediate engineering lesson.
It strengthens it:

> Canonicalization should be tied to the current world and opponent support, not hard-coded once forever.

## Implementor guidance

1. Add genotype-to-phenotype canonicalization before ranking rematch-world search results.
2. Keep `mem1_exit_after_break_v1` (`CCEEE`) as the human-readable representative of the `CCE**` family.
3. Report both raw discoveries and canonical families so search progress is not inflated by aliases.
4. Recompute the canonicalization map whenever the rematch world adds new opponent families or new sources of stochastic reachability.

The practical handoff is simple:

> When the endogenous rematch world lands, do not just score policies. Deduplicate them by reachable behavior in that world.
