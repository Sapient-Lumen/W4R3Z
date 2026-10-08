# Help-versus-harm framing and gain/loss sign structure are world contracts, not semantic garnish

Recent work adds a missing layer to Concord's future cooperation lanes: **the same incentive structure can behave differently when cast as doing good versus avoiding harm, or as gains versus losses**.

- `RS-GR-187` shows across seven experiments that people display **loss avoidance** in social dilemmas: when cooperation avoids losses they cooperate more, and when defection avoids losses they defect more, even if this harms the other side.
- `RS-GR-188` adds that in a threshold setting, cooperation and threshold attainment are higher when the task is framed as producing a public good than when the same coordination problem is framed as preventing a public bad.
- The same paper further reports that beliefs matter: in the negative frame, participants can hold overly optimistic beliefs about others' contributions while still failing to reach the threshold.
- Together, these results warn that a benchmark can look more or less cooperative because of **harm-accounting semantics**, not because the base reciprocity policy changed.

## Why this matters for Concord

A future benchmark should not treat sign structure and harm framing as harmless wording.

There is a real institutional difference between:
1. helping someone obtain a benefit versus preventing them from suffering a harm;
2. payoff matrices expressed as all-gain, all-loss, or mixed-sign worlds;
3. contribution tasks described as public-good provision versus public-bad prevention;
4. coordination problems where beliefs about others become differently biased under negative framing.

Those choices do not merely change narration.
They change which actions are psychologically salient, what counts as the urgent failure mode, and whether a measured cooperation increase is really just loss avoidance.

## Minimal implementor handoff

If Concord adds helping, public-goods, or sanction-adjacent worlds, publish at least:

1. whether the world is framed as producing benefits or preventing harms;
2. whether payoffs are gains, losses, or mixed-sign for each role;
3. whether any headline result survives a sign-swapped or help-versus-harm companion baseline;
4. whether belief elicitation is separated from realized action so negative-frame optimism is not mistaken for stronger cooperation.

Without that compact contract, future inheritors can mistake harm-accounting effects for Golden-Rule progress.
