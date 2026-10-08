# rev0033 action-counterfactual ranker

rev0033 adds the first gameplay-action counterfactual dataset. Previous gameplay rankers were either imitation models or outcome-weighted behavior cloning. Those methods observe which action a behavior policy chose and whether the trajectory later won, but they do not directly evaluate legal actions that were not chosen.

The new collector samples public `DecisionFrame`s from ordinary behavior games. At a sampled frame, the collector copies the true referee state, branches each manageable legal action, and rolls out each branch with public agents. The agent under training never sees that true state; the true-state copy exists only inside the offline label generator.

The first smoke setting is deliberately small:

```text
behavior games:              8
sampled situations:          18
candidate actions:           47
branch games:                94
branch rollouts per action:  2
high-action frames skipped:  1
```

Each candidate row records:

```text
public context features
stable action features
mean actor score from branch rollouts
best action score in that frame
value gap to best
whether the behavior policy's chosen action was empirically best
```

The immediate result is not a strong player. The model trained from this tiny set had weak held-out listwise accuracy:

```text
test top-1 best-action accuracy: ~0.167
random tied-best baseline:       ~0.569
test RMSE:                       ~0.423
```

That failure is useful. It says the seam is right, but the label budget is far too small. The right next move is more situations and more rollouts, not model cleverness.

The rev0033 frozen model is still evaluated as an ordinary public strategy:

```text
counterfactual_linear_ranker_rev0033
counterfactual_ranker_blend_threat_rev0033
counterfactual_ranker_blend_counter_rev0033
counterfactual_ranker_blend_patient_rev0033
```

The payoff smoke table passed promotion/statistical/replay/C++ gates, but it is not a strategy claim. The strongest counterfactual-ranker variant in the smoke table was mid-pack.
