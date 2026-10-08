# rev0042 experiment matrix additions

New experimental axis:

```text
label allocation method
  fixed_equal_3
  adaptive_race_prefix
```

Controlled constants in the archived smoke run:

```text
hard-frame queue: public-only
branch source: Python semantic referee
C++ role: transition shadow checker
branch rollouts generated per action: 3
adaptive base rollouts: 1
adaptive extra budget: 6
minimum decisive margin: 0.20
```

Primary metrics:

```text
adaptive rollout savings
fixed decisive situations
adaptive decisive situations
best-set agreement rate
adaptive changed label situations
decisive labels per 100 rollouts
C++ skipped/mismatch count
branch truncations
```

Useful future expansion:

```text
compare fixed_equal_5 vs adaptive_race_prefix
compare hard-frame queue vs random choice-frame queue
compare ranker-prior-assisted adaptive racing vs pure score-margin racing
```
