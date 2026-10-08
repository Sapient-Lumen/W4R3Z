# Life-20 pilot stress — rev0059

The seed-disjoint A-D run contradicted the rev0058 life-20 pilot-swap read.  Instead of treating that as noise or burying it, rev0059 adds a targeted life-20 A/B stress pass.

## Stress pass

```text
arms: A_original_size_skew vs B_pilot_swap_size_skew
life: 20 only
games: 96
base_seed: 5959200
reps per arm/seat/start: 12
max_decisions: 900
truncations: 0
C++ chosen-transition rows checked: 27,500
C++ mismatches/skips: 0 / 0
replay samples passed: 8 / 8
```

Stress-only result:

| arm | games | target score |
|---|---:|---:|
| A_original_size_skew | 48 | 0.7708 |
| B_pilot_swap_size_skew | 48 | 0.3125 |

Stress-only delta:

```text
original_minus_pilot_swap = +0.4583
```

Combined life-20 A/B evidence across rev0058 focused A-D, rev0059 A-D, and rev0059 stress:

| arm | games | target score |
|---|---:|---:|
| A_original_size_skew | 84 | 0.7619 |
| B_pilot_swap_size_skew | 84 | 0.4167 |

Combined life-20 A/B delta:

```text
original_minus_pilot_swap = +0.3452
```

## Interpretation

The life-20 contradiction is not fatal to the shell/endurance story, but it means the mechanism is not a single scalar.  The best current read is:

```text
life 40: shell/endurance interpretation is stable.
life 20: A/B pilot-swap has seed sensitivity, but the added stress pass pulls cumulative evidence back toward shell/endurance.
C/D equalization: removing the 60-vs-40 asymmetry weakens the original edge, especially in life 20.
library-out: remains the dominant winning mechanism.
```

The next risk is not “write a better claim card.”  It is to isolate why the life-20 pilot swap can sometimes perform like the original.  That likely requires transition-level feature auditing of draw/Jace/counter timing in the contradictory seeds.
