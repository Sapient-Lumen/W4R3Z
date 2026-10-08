# rev0025 outcome ranker results

## Training collection

```text
games:                  112
terminal games:         112
truncated games:        0
decisions:              29,831
candidate rows:         64,897
max legal actions:      37
mean legal actions:     ~2.1755
winning chosen rows:    14,343
losing chosen rows:     15,488
```

## Weighted classifier

```text
model:                  logistic regression
feature count:          81
weighting:              win 1.0 / loss 0.15 / truncation 0.0
test top-1:             ~0.9106
random baseline:        ~0.7230
MRR:                    ~0.9430
```

Top coefficient magnitudes were mostly board/choice/target features.  That is a useful audit signal: the model is not merely learning one action slot id.

## Payoff smoke standings

```text
1. outcome_counter_wall      0.703125
2. pub_counter_wall          0.671875
3. code_jace60               0.609375
4. pub_threat_overlord       0.484375
5. outcome_fjace             0.421875
6. mlp_fjace                 0.406250
7. mlp_threat_fovr           0.406250
8. outcome_threat_fovr       0.296875
```

Interpretation: outcome weighting can produce a useful policy on at least one shell (`sixty_counterwall_jace`), but it is not universally good.  Deck/pilot pairing still matters.
