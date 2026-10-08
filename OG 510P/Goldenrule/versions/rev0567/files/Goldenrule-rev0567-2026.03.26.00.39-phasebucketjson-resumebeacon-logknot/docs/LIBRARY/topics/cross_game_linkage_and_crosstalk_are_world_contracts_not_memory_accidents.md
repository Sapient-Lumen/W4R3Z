# Cross-game linkage and crosstalk are world contracts, not memory accidents

Recent work adds a second missing layer to Concord's future reciprocity lanes: **what happens in one lane can be allowed to discipline, contaminate, or excuse behavior in another**.

- `RS-GR-181` shows that when players can link concurrent games, they can use cooperation in a more valuable lane as leverage to sustain cooperation in a lower-benefit lane.
- The paper further identifies linked strategies that respond to a defection in one lane by reducing cooperation in both lanes, which means retaliation rights can cross institutional boundaries.
- `RS-GR-182` shows that crosstalk between concurrent repeated games impedes cooperation, shrinks the basin of cooperative play, and can make harsh retaliators such as Tit-for-Tat perform poorly unless forgiveness is adjusted.
- Together, those results show that cross-lane dependence is not generic noise: it determines whether spillovers behave like strategic linkage, memory confusion, or upstream retaliation.

## Why this matters for Concord

A future benchmark should not hide lane linkage inside a broad "memory" or "noise" label.

There is a real institutional difference between:
1. fully isolated lanes with channel-specific memory;
2. lanes that are strategically linkable on purpose;
3. lanes that spill into each other through imperfect recall or crosstalk;
4. worlds where retaliation, forgiveness, or repair are allowed to generalize across domains.

Those choices do not merely change implementation detail.
They change whether a defection in one place licenses punishment somewhere else, whether forgiveness must be stronger to prevent cascade failures, and whether observed cooperation comes from local reciprocity or from borrowed leverage.

## Minimal implementor handoff

If Concord adds concurrent or multi-domain reciprocity worlds, publish at least:

1. whether lanes are isolated, intentionally linked, or subject to accidental crosstalk;
2. whether retaliation, forgiveness, and repair can transfer across lanes;
3. whether memory is channel-specific or pooled across relationships;
4. whether at least one channel-isolated baseline is kept beside any linked or spillover lane.

Without that compact contract, future inheritors can mistake cross-lane leverage or memory contamination for reciprocal virtue.
