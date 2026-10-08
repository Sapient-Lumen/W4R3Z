# Collective reputation and stereotype scope are world contracts, not just cognitive shortcuts

Recent group-structured reciprocity work adds a compact warning for any Concord lane that lets reputations attach to teams, communities, or coarse identity tags instead of only to individuals.

- `RS-GR-146` shows that when indirect reciprocity is lifted from dyads into public-goods settings with **collective reputations**, changing the group-assessment criterion can destabilize or sustain cooperation, and that a moderately strict criterion can be best.
- `RS-GR-147` shows that replacing individual reputations with **stereotyped group reputations** can either help or hurt cooperation depending on how widely information is shared, and stereotype reliance can become sticky when individual reputation is costly or noisy.

## Why this matters for Concord

A future reputation lane should not assume that “group reputation” is just a compressed view of many individual reputations.

Once reputations are allowed to live at group scope, three institutional choices appear:

1. whether updates attach to individuals, groups, or both,
2. whether observers may substitute group stereotypes when individual evidence is sparse or costly,
3. and how strict the group-assessment rule is when members inside the same group behave differently.

Those are not cosmetic details.
They decide whether the benchmark is rewarding trustworthy individuals, punishing whole groups for one member, or quietly allowing stereotype caching to stand in for real observation.

## Minimal implementor handoff

If Concord adds any group-structured or collective-reputation lane, publish at least:

1. the reputation carrier set (individual-only, group-only, or dual-layer),
2. whether observers may fall back to group stereotypes when individual records are missing or expensive,
3. the collective-assessment rule for mixed-behavior groups,
4. whether stereotype use is exogenous, optional, or adaptive,
5. one individual-reputation baseline before generalizing from group-level results.

Without that compact contract, future sessions can mistake stereotype compression or group-pooling effects for stronger reciprocity.
