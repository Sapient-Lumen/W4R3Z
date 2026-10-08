# Reputation governance topology is a world contract, not just an implementation choice

Recent work adds a missing institutional layer for Concord's future reputation lanes: **who holds reputations, how much they agree, and how opinions become shared**.

- `RS-GR-150` shows that cooperation under indirect reciprocity depends on how correlated individual opinions become.
- The paper reports that no cooperative norm is evolutionarily stable when individual opinions are statistically independent.
- That means the difference between fully private opinions, partially synchronized opinions, and effectively public consensus is not bookkeeping. It changes whether indirect reciprocity can work at all.
- `RS-GR-151` adds that the *way* agents combine private and public reputations matters too.
- When agents prioritize public information and use friend-and-enemy heuristics, the paper reports polarization cycles with high cooperation, invasion by defectors, and later fragmentation.
- More private weighting reduces polarization and defector invasion, but also yields more limited cooperation.
- Friend-focused use of reputation plus past experience is the combination the paper reports as producing more stable cooperative populations.

## Why this matters for Concord

A reputation world should not treat governance topology as an invisible backend choice.

There is a real institutional difference between:
1. each agent carrying mostly private views;
2. agents partially synchronizing via gossip or shared observation;
3. a world exposing a near-public or centralized consensus reputation.

Those topologies do not merely change storage.
They change whether disagreement, conformity, polarization, and norm enforcement are even comparable.

## Minimal implementor handoff

When Concord adds richer reputation lanes, the world contract should declare:

1. whether reputation is private, partially synchronized, public-consensus, or centrally assigned;
2. how synchronization happens (cadence, source pool, merge rule, and whether direct experience can resist or override consensus);
3. whether agents weight only trusted/friendly sources or also hostile / enemy sources;
4. whether fresh private evidence can reopen a consensus judgment or whether the world freezes around a shared score.

Without that publication layer, future results can mistake governance topology for moral or strategic superiority.
