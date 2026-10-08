# The first retained rematch-world benchmark should carry a paired-ranking interpretation handoff

The archive already has the three proxy-era ingredients needed to answer the practical leaderboard question cleanly:

- occupancy accounting in `artifacts/reports/rematch_proxy_occupancy_accounting_snapshot_20260306.{md,json}`,
- turnover scaling in `artifacts/reports/rematch_proxy_turnover_tempo_snapshot_20260306.{md,json}`,
- and raw-vs-normalized rank decomposition in `artifacts/reports/rematch_proxy_rank_decomposition_snapshot_20260306.{md,json}`.

But without one compact **benchmark-facing handoff**, a future inheritor still has to reopen all three just to answer the implementor question:

> when the raw leaderboard moves, is that probably a true within-match strategy improvement, or mostly an occupancy / tempo artifact?

A retained benchmark seed should therefore carry one tiny copied paired-ranking interpretation handoff instead of forcing the next session to reconstruct the answer from scratch.

## What the copied handoff should keep

Only the decision-relevant parts need to survive:

1. the canonical occupancy-normalized order `CCEEE > CCDDE > DCECC > always_c > courteous_firm`,
2. the fact that this normalized order is identical across the tested extortion shares `20`, `50`, and `80`,
3. the count of raw-vs-normalized disagreements in nonzero-delay panels (`3` of `6`, with `4` total pairwise inversions),
4. the sharpest disagreement panel (`extortion=20, delay=2`, Kendall tau `0.6`, `2` pairwise inversions),
5. the occupancy fact that delay losses are overwhelmingly share losses (mean share-explained fraction `0.985842`),
6. the tempo fact that the highest-churn delay-2 cell loses about `4.877836x` as much matched share as the lowest-churn cell,
7. and one explicit interpretation rule saying that raw-only movement should default to an **occupancy / tempo artifact** until normalized rankings move too.

## Why this belongs inside the benchmark seed

The benchmark already intends to publish:

- occupancy rows,
- turnover rows,
- and paired leaderboards.

What it still lacked was a compact frozen packet telling the inheritor how those three surfaces fit together.
Without that packet, the archive still leaks interpretation burden into future sessions.

Treat the copied handoff as a frozen citation surface inside the benchmark seed until the engine can emit a real world-native ranking explanation manifest.
