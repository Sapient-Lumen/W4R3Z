# rev0033 priority reconsideration

The previous priority was no-choice segment benchmarking and larger MAP-Elites races. rev0033 changed the immediate priority because the learned gameplay rankers had a deeper weakness: they did not know the value of unchosen legal actions.

The new priority is:

```text
1. Scale gameplay action-counterfactual labels: more situations, more branch rollouts.
2. Use branch labels to train a better value/ranker target; current rev0033 model is too small/noisy.
3. Keep C++ shadow checks attached to all branch/evaluation traffic.
4. Return to no-choice segment execution benchmarks after branch data becomes expensive enough to need acceleration.
5. Then run larger MAP-Elites/meta-rank races using counterfactual-trained policies.
```

The main lesson this turn: unchosen-action labels are the right shape, but the first label budget is tiny. The current model's weak held-out accuracy is a warning, not a failure of the direction.
