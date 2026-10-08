# rev0031 repeated counterfactual scale probe

rev0030 proved the repeated opening-hand counterfactual shape but used a tiny label budget:

```text
24 paired opening situations
2 branch rollouts per keep/mulligan branch
```

rev0031 modestly scales that to:

```text
36 paired opening situations
3 branch rollouts per keep/mulligan branch
216 branch games
55,566 C++-checked branch transitions
0 skipped C++ transitions
0 C++ mismatches
0 truncations
```

This revision does not train a new mulligan policy. It is a label-budget diagnostic. The point is to measure whether repeated rollouts are giving cleaner keep-vs-mulligan signals before spending more effort on a new model.

Observed branch labels:

```text
mulligan-better pairs: 9
keep-better pairs:     9
tie pairs:            18
mean mulligan-minus-keep: +0.0556
mean absolute delta:       0.3333
```

The important lesson is that the branch label is still contextual and noisy. Mulligan learning should continue moving toward paired/counterfactual rollouts, but the next improvement is more data and possibly branch rollout common-random-number controls, not a cleverer model on tiny labels.
