# rev0034 experiment matrix additions

New experiment family:

```text
scaled gameplay action counterfactuals
```

Axes:

```text
sampled situations
branch rollouts per action
branch rollout horizon
max legal actions per sampled frame
behavior-policy source population
label-confidence threshold
ranker family: linear / MLP / boosted / code-policy prior blend
```

Questions:

```text
Does behavior-chosen-best rate improve as behavior policies improve?
Do high-confidence branch labels predict payoff better than all branch labels?
Does a simple linear ranker benefit from counterfactual labels, or does it need a non-linear/listwise model?
Are the most valuable counterfactual situations mostly RESPONSE windows, Jace activations, attacks, or discard choices?
Which legal-action classes are systematically misplayed by current public/code policies?
```
