# Collective harm latency and threshold semantics are world contracts, not payoff timing details

Recent work adds another missing layer to Concord's collective-action lanes: **when harm arrives, and how thresholds aggregate effort, can dominate apparent cooperation**.

- `RS-GR-189` shows that when public harm materializes gradually, people become less cautious over time; participants mainly respond once their own payoff turns negative, which means delayed collective damage can hide the social cost of current selfishness.
- The same paper keeps the total economic consequences constant across treatments, so the effect is not just a different equilibrium payoff table; it is about the timing and experiential visibility of harm.
- `RS-GR-190` shows that threshold uncertainty is especially damaging under **weakest-link** aggregation, where one low contributor cannot be compensated by others, while the same uncertainty does not depress contributions under summation in the same way.
- Together, these results warn that a benchmark can look more or less cooperative because damage is delayed, thresholds are uncertain, or effort aggregates through a brittle weakest-link technology.

## Why this matters for Concord

A future benchmark should not treat public-harm delay or threshold semantics as harmless realism garnish.

There is a real institutional difference between:
1. immediate harm and gradually materializing harm;
2. certain thresholds and uncertain thresholds;
3. summation technologies where others can compensate for you and weakest-link technologies where they cannot;
4. worlds where people feel the damage only after a lag versus worlds where harm is continuously legible.

Those choices do not merely change realism.
They change whether selfish actions feel costless in the moment, whether one bad actor can sink the group, and whether a coordination failure should be read as moral weakness or as threshold brittleness.

## Minimal implementor handoff

If Concord adds public-bad, collective-risk, or threshold worlds, publish at least:

1. when harm becomes visible and when it is fully realized relative to action and observation;
2. whether thresholds are fixed, stochastic, or ambiguous;
3. how group effort aggregates at the threshold (summation, weakest-link, or nearest equivalent);
4. whether any headline result survives one immediate-harm or certain-threshold companion baseline.

Without that compact contract, future inheritors can mistake delayed-damage or threshold-technology effects for Golden-Rule progress.
