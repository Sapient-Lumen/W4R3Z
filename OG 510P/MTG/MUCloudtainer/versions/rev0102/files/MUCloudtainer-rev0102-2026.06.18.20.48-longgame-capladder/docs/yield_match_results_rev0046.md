# rev0046 matched yield/hard/margin queue results

rev0046 compares three public queue selectors on a shared candidate pool:

```text
hard_screen
margin_screen
yield_screen
```

All three selectors see the same public hard-frame pool.  Only the union of their selected frames is branched, so every selector is scored from the same branch outcomes.

## Smoke result

```text
behavior games:              26
behavior decisions:       5,330
choice frames seen:       2,497
pool rows:                   36
hard selected:               10
margin selected:             10
yield selected:              10
union selected:              20
overlap all three:            4
branch games:               176
branch truncations:           0
C++ checked transitions: 20,453
C++ skipped transitions:      0
C++ mismatches:               0
```

Selector results:

```text
hard_screen:   1 decisive / 90 rollouts  = 1.111 decisive per 100
margin_screen: 3 decisive / 90 rollouts  = 3.333 decisive per 100
yield_screen:  3 decisive / 86 rollouts  = 3.488 decisive per 100
```

The yield queue slightly beat the margin queue in this smoke run and beat the hard queue clearly.  This should be read as a promising queueing result, not a gameplay claim.

## Pushback

The training set is still small.  The holdout signal exists, but it is noisy:

```text
top-quartile yield per 100: 6.389
baseline yield per 100:    4.402
```

This is enough to justify keeping the yield screen in the labeler toolkit.  It is not enough to claim that the model has solved frame selection.
