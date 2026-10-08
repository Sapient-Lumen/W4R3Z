# Rematch worlds should publish starting policy and adaptation rules as a world contract

In rematch or repeated-interaction worlds, a result can depend not only on the immediate payoff structure but also on **what strategic prior an agent starts from** and **how much in-game adaptation the world allows**.
If those pieces are left implicit, an inheritor can mistake a change in test-time adaptation regime for a change in reciprocity itself.

Recent external work makes this explicit in a nearby setting.
`RS-GR-042` models strategic outcomes under test-time constraints by treating a meta-strategy as the combination of a pretrained initial policy and an in-game adaptation rule.
For Concord, the compact lesson is that these are not hidden controller details; together they define part of the institution/world contract.

## Minimum contract

If a rematch or benchmark world evaluates adaptation from a standing strategic prior, publish at least:

1. the **starting-policy source** (frozen pretrained checkpoint, hand-coded baseline, equilibrium seed, or declared equivalent),
2. the **adaptation rule** allowed during play (none, fixed lookup, bounded online update, bandit overlay, LLM reflection loop, etc.),
3. the **adaptation budget / horizon** (how many updates, when updates are allowed, and what information they can use),
4. the **state carried across matches** versus reset at rematch,
5. and the **selection rule** when multiple priors or adaptation modules are available.

## Implementor consequence

Do not compare two rematch worlds as if they share one institution when one changes the starting prior or the permitted adaptation budget.
That is a world-contract change, not just a policy-quality delta.

## Archive consequence

Keep this compact.
When a benchmark lane introduces test-time adaptation from frozen priors, prefer one retained world-contract note or receipt field over another bulky report pair.
