# Monitoring and evidence-transfer costs are world contracts, not background friction

Recent work adds a missing institutional layer for Concord's future trust and reputation lanes: **information is not free to gather, hold, or share**.

- `RS-GR-153` models trust as a reduced-monitoring heuristic rather than as cooperation itself.
- The paper reports that when monitoring is costly, trust-based strategies can raise cooperation by reducing the need to keep checking a partner every round.
- It also reports that the same heuristic can help under action error, which means observed cooperation gains can partly come from cheaper monitoring rather than from more benevolent action policy.
- `RS-GR-154` adds that direct transfer costs and competition costs reduce information sharing in laboratory markets.
- The paper reports that while information sharing improves trust and market efficiency, both direct transfer costs and competition pressure substantially reduce sharing.
- It further reports that players react strategically to those information-transfer conditions, so evidence friction changes both the supply of reputation information and the behavior of those being watched.

## Why this matters for Concord

A trust or reputation world should not silently assume that observation and evidence-sharing are free.

There is a real institutional difference between:
1. always-on cheap monitoring;
2. costly or sampled monitoring;
3. costly or competitively disincentivized gossip / evidence transfer.

Those differences do not merely change runtime cost.
They change what "trust" means, whether reputation can form densely enough to matter, and whether cooperation gains are really policy gains or just monitoring-economy gains.

## Minimal implementor handoff

When Concord adds richer trust or reputation lanes, the world contract should declare:

1. whether observation is continuous, sampled, threshold-triggered, or strategically optional;
2. what it costs to monitor, remember, or forward information about others;
3. whether evidence-sharing creates competitive disadvantage or other indirect costs;
4. whether trust metrics are separated from cooperation metrics so reduced monitoring is not mistaken for improved goodwill.

Without that publication layer, future results can mistake information economics for moral or strategic superiority.
