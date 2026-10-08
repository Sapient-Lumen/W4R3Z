# rev0029 counterfactual mulligan ranker

rev0029 turns the rev0028 paired opening-hand branch data into a first usable policy:

```text
mulligan_counterfactual_ranker_rev0029
```

The key difference from earlier mulligan agents is the label source.

Earlier agents learned from:

```text
pseudo-oracle hand quality
terminal outcomes attached to behavior-policy choices
```

The rev0029 model learns from:

```text
same first seven-card look
  forced KEEP branch
  forced TAKE-MULLIGAN branch
compare terminal score
```

The target is:

```text
mulligan_score - keep_score
```

Positive predictions take the first mulligan. Negative predictions keep.

## Conservative contract

The model is **first-look only**. It does not pretend to know later London-mulligan decisions from first-look branch data.

```text
first keep/take decision: counterfactual ridge model
later keep/take decisions: delegated to mulligan_outcome_ranker_rev0027
bottom-card choices: delegated to mulligan_outcome_ranker_rev0027
```

This keeps the learned component honest: it uses counterfactual information only where that information exists.

## Smoke result

Training source:

```text
72 rev0028 paired opening situations
15 keep-better rows
18 mulligan-better rows
39 tie rows
```

Model smoke metrics:

```text
test decision accuracy with ties counted correct: about 0.833
test non-tie sign accuracy: about 0.500
test RMSE: about 0.972
```

The non-tie sign accuracy is weak. That is not hidden. The data is tiny, noisy, and branch rollouts are one-sample. The value of this revision is the method seam, not proof that the policy is strong.

## Payoff gate

Same-shell panel:

```text
3 deck/pilot shells
6 mulligan policies each
432 games
8 replay traces
2,206 C++ trace events
0 C++ skipped events
0 C++ mismatches
0 truncations
promotion gate passed
statistical gate passed
```

The counterfactual policy performed well in the `fjace_code` shell, poorly in `overlord_threat`, and middling in `wall_counter`. That shell dependence is the important lesson: mulligan policy is part of the strategy bundle, not an independent universal setting.
