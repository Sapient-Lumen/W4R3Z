# Seed-disjoint decomposition — rev0059

rev0059 moves the rev0058 decomposition from a directional panel into a seed-disjoint confirmation attempt focused on the four riskiest explanatory arms:

```text
A_original_size_skew
B_pilot_swap_size_skew
C_equalized_40v40
D_equalized_60v60
```

The goal was not to promote a general claim.  The goal was to see whether the previous read — “edge follows counter-wall / 60-card endurance shell more than the cf34 pilot” — survives new seeds.

## Seed-disjoint A-D run

```text
games: 160
base_seed: 5959000
reps per arm/life/seat/start: 5
max_decisions: 900
truncations: 0
C++ chosen-transition rows checked: 47,323
C++ mismatches/skips: 0 / 0
replay samples passed: 12 / 12
```

Target-perspective scores:

| life | original size-skew | pilot swap | equalized 40v40 | equalized 60v60 | immediate read |
|---:|---:|---:|---:|---:|---|
| 20 | 0.700 | 0.700 | 0.400 | 0.350 | contradicted rev0058; pilot not rejected in this seed block |
| 40 | 0.600 | 0.300 | 0.600 | 0.400 | supports shell/endurance over pilot |

The life-40 story replicated directionally.  The life-20 story did not: the pilot-swap arm tied the original size-skew arm in this seed block.

## Combined rev0058 + rev0059 A-D read

The combined A-D comparison before the stress pass was:

| life | original | pilot swap | 40v40 | 60v60 | read |
|---:|---:|---:|---:|---:|---|
| 20 | 0.750 | 0.556 | 0.389 | 0.500 | size/skew or mixed mechanism, not a clean pilot rejection |
| 40 | 0.639 | 0.306 | 0.528 | 0.444 | shell/endurance favored |

## What this changes

rev0058 was too simple.  rev0059 says the shell/endurance interpretation is still strong at life 40, but life 20 has seed sensitivity.  That is precisely the kind of contradiction the cube should surface rather than smooth over.
