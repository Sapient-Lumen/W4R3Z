# rev0039 screen-match results

Archived smoke run:

```text
behavior games:              14
choice frames seen:          27
frames with disagreement:    14
sampled situations:          14
full-menu situations:         8
subset situations:            6
union candidate actions:     51
branch games:               102
branch rollouts/action:       2
branch truncations:           0
C++ checked transitions:  24,373
C++ skipped transitions:      0
C++ mismatches:               0
```

Matched selector result:

```text
union decisive situations:              7
screened better situations:             0
unscreened better situations:           2
tied method situations:                12
mean screened-minus-unscreened score:  -0.0714
screened hits union-best rate:          0.8571
unscreened hits union-best rate:        1.0000
screen-vote hits union-best rate:       0.7857
behavior chosen hits union-best rate:   0.5000
```

Interpretation:

```text
Disagreement screening still looks useful for choosing frames.
But when the branch budget is tight, simple vote priority can lose to the older diversity selector.
```

That suggests the next selector should combine:

```text
public disagreement
+ action diversity
+ behavior action
+ cheap prior/ranker score
+ adaptive extra rollouts when top actions are uncertain
```

This revision deliberately does not promote a rev0039 policy.  It is an audit/selector revision.
