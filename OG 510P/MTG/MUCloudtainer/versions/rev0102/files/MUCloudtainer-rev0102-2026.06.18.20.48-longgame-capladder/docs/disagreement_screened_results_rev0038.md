# rev0038 results — disagreement-screened label quality

Archived smoke collection:

```text
behavior games:                 12
behavior decisions:             54
screen frames with choices:     29
screen frames with disagreement:14
sampled situations:             14
candidate actions:              61
branch games:                   122
branch rollouts per action:     2
branch truncations:             0
C++ checked branch transitions: 23,401
C++ skipped transitions:        0
C++ mismatches:                 0
```

Label audit:

```text
decisive situations:            6 / 14
mean margin:                    ~0.321
mean label confidence proxy:    ~0.360
behavior chosen-best rate:      ~0.357
screen-voted-best rate:         ~0.643
mean unique screen votes:       ~2.143
```

That is the useful signal: screen votes were more likely than the behavior policy to include an empirically best branched action.  This is not a proof of strategic strength, but it suggests disagreement screening is a better label-budget heuristic than sampling arbitrary manageable frames.

The rev0038 ranker was trained from these labels and evaluated as an ordinary public strategy.  Its tiny holdout metrics were weak:

```text
test top-1 best-action accuracy: ~0.400
random best-action baseline:     ~0.400
test MRR:                        ~0.667
```

So the revision should be read as an infrastructure/label-quality improvement, not a new champion policy.

Promotion-gated smoke payoff:

```text
strategies:              6
payoff games:            144
replay samples:          8 / 8 passed
C++ shadow events:       40,141
C++ skipped events:      0
C++ mismatches:          0
truncations:             0
promotion gate:          passed
statistical gate:        passed
```

The payoff table is clean enough to archive, but still too small for MUC theory claims.
