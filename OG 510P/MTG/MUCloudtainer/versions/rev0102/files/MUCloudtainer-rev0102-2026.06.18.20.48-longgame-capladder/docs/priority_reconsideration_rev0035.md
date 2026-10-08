# Priority reconsideration after rev0035

The last few revisions showed that action-counterfactual learning is the right
shape, but the bottleneck is not the model.  It is label budget and label
quality.

Revised priority order:

```text
1. Budgeted/search-style branch selection for high-action frames.       done rev0035 first pass
2. Increase decisive action-counterfactual labels, not just row counts.
3. Add branch allocation/racing: spend extra rollouts where labels are uncertain.
4. Run larger MAP-Elites races including rev0035/rev0034/counterfactual policies.
5. No-choice segment execution benchmark under Python pre/post SIGv2 gates.
6. Meta-rank over denser, nontruncated promoted payoff tables.
```

Pushback on rev0035: the budget selector made high-action frames visible, but the
archived labels were mostly ties.  The next improvement should be adaptive branch
allocation or different branch rollout opponents, not a more complicated model.
