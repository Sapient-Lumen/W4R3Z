# Endogenous rule choice and democratic selection are world contracts, not preplay ceremony

Recent work adds a missing governance layer to Concord's future sanction, allocation, and institution-design lanes: **it matters whether a rule is imposed from outside or chosen by the agents who must live under it**.

- `RS-GR-203` revisits the classic democracy-effect problem and shows that, after accounting for selection, democratic choice can directly increase cooperation in a strategic-interaction setting rather than merely sorting different types of people into different rules.
- `RS-GR-204` shows that formal democratic sanction mechanisms can increase public-good contributions, but the effect depends on the mechanism and on whether voting is individual or group-level.
- `RS-GR-206` adds an important caution: endogeneity is **not** a universal premium. In a large student lab-in-the-field study, exogenously imposed institutions outperformed endogenously chosen ones across reward and punishment rules.
- Together, these results warn that a benchmark can look more cooperative, more legitimate, or more compliant because agents had a say in the rule, not because the rule itself is intrinsically better.

## Why this matters for Concord

A future benchmark should not collapse all governance setups into one generic “institution present” switch.

There is a real institutional difference between:
1. an externally imposed rule;
2. a binding group vote over the rule;
3. an advisory vote whose result is later overridden or filtered;
4. a world where the same sanction or allocation rule exists, but agents never participate in selecting it.

Those are not preplay cosmetics.
They change legitimacy, anticipatory compliance, and what the observed cooperation is actually evidence of.

## Minimal implementor handoff

If Concord adds rule choice or policy voting, publish at least:

1. whether the rule is exogenous, endogenously chosen, or only nominally voted on;
2. whether votes are advisory, binding, or sometimes overridden;
3. whether headline results survive an exogenous-imposition baseline beside the endogenous-choice lane;
4. whether the same policy effect remains once mechanism choice is separated from mere self-selection into preferred rules.

Without that compact contract, future inheritors can mistake democratic selection or legitimacy effects for Golden-Rule progress.
