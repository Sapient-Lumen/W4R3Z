# Scarce allocation rules and planner authority are world contracts, not post hoc accounting

Recent work adds a missing scarcity layer for Concord's future helping and redistribution lanes: **once multiple claimants compete for limited goods, the allocation rule is part of the institution, not a neutral accounting step after cooperation happens**.

- `RS-GR-163` reports that when people allocate a fixed sum across multiple claimants, they weigh merit, need, and equality together rather than applying one universal fairness rule.
- The paper further reports that higher-status respondents tend to generate more unequal allocations, while respondents who perceive inequality as excessive allocate more equally.
- `RS-GR-164` reports that in an iterated multiplayer trust problem, a learned social planner can outperform baseline allocation mechanisms by conditioning generosity on available resources and temporarily sanctioning defectors.
- `RS-GR-165` adds that third-party allocators can improve efficiency relative to automatic equal division, but inequality makes allocator incentives less effective because fairness ideals come into conflict.

## Why this matters for Concord

A future benchmark should not collapse scarcity governance into one vague redistribution score.

There is a real institutional difference between:
1. automatic equal division of scarce goods;
2. need-weighted allocation;
3. merit- or contribution-weighted allocation;
4. history-sensitive allocation that conditions on reciprocity or defection;
5. decentralized self-allocation versus third-party or planner-controlled allocation.

Those choices do not merely change downstream welfare summaries.
They change who has authority, which claims are legible, whether scarcity is softened or amplified by design, and whether apparent cooperation is really coming from agent virtue or from a planner that redistributes and sanctions in the background.

## Minimal implementor handoff

When Concord adds scarce-help, redistribution, or group-production lanes, the world contract should declare:

1. who allocates the scarce good: recipients, peers, a third-party allocator, or a centralized planner;
2. which allocation principles are live: equality, need, merit, reciprocity history, punishment history, or hybrids;
3. whether allocation is static, queue-based, threshold-triggered, or state-dependent on available resources;
4. whether the allocator may punish, withhold, or condition future access based on prior behavior.

Without that publication layer, future results can mistake planner design, queue discipline, or scarcity-allocation rules for genuine reciprocity gains.
