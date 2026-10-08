# Cooperation benchmark LLM lanes should publish incentive instructions and payoff scaling

LLM-only cooperation benchmarks should not treat the incentive contract as invisible prompt plumbing.
Recent experimental-economics-for-LLMs work shows that strategic behavior can move when the benchmark changes the stated payment rule, the size of the payoffs, or the surrounding language that frames those payoffs.

So when a cooperation benchmark scores LLM or agent-only lanes, the compact card should publish one small incentive row with at least:

1. the exact **decision incentive instruction** shown to the model (for example, maximize points, maximize money, help the partner, or mixed goals);
2. whether rewards are **hypothetical, simulated, real-through-tooling, or inherited from a larger task scaffold**;
3. the **payoff matrix or reward function actually shown to the model**, including any scaling or normalization;
4. any **conversion rule** from points to money / utility / prize probability when the benchmark tries to mirror a human experiment;
5. whether the lane changed only payoff magnitude, only wording, or both.

Do not compare or pool LLM-lane cooperation scores across studies if their incentive wording or payoff scale differs but the card hides that difference.
A model can look more cooperative, more rational, or more stable partly because the benchmark changed stake salience or reward framing, not because the underlying cooperation capability improved.

One compact row is enough: incentive instruction, reward semantics, payoff scaling, and conversion rule.
That keeps future inheritors from laundering an incentive-contract change into a policy-generalization claim.
