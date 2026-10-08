# Decomposition results — rev0058

Codename: `deckpilotablate-endurancegate`

## What changed

rev0058 moves from mission audit to a concrete decomposition of the rev0056 claim.  It asks whether `cf34_counter_wall` beat `pub_threat_overlord` because of the cf34 pilot, the counter-wall deck shell, the 60-vs-40 deck-size asymmetry, or the terminal library-out mechanism.

This is intentionally not a new promotion claim.  It is a small explanatory panel with target-perspective scores.

## Validation

```text
games: 192
max decisions: 900
truncations: 0
C++ chosen transitions: 58172
C++ skipped / mismatches: 0 / 0
C++ trace skipped / mismatches: 0 / 0
replay samples passed: 8 / 8
decomposition gate: True
```

rev0058 deliberately ships only `data/rev0058_decomposition_cpp_transition_sample.csv` rather than the full generated transition table.  The run generated `58172` C++-checked chosen transitions, all matched, but the cube keeps only a compact sample to reduce raw evidence ballast.

## Comparison table

| Life | Original | Pilot swap | 40v40 | 60v60 | same counter60 pilot | same overlord40 pilot | Provisional read |
|---:|---:|---:|---:|---:|---:|---:|---|
| 20 | 0.812 | 0.375 | 0.375 | 0.688 | 0.562 | 0.688 | edge_follows_counterwall_deck_shell_more_than_cf34_pilot |
| 40 | 0.688 | 0.312 | 0.438 | 0.500 | 0.688 | 0.438 | edge_follows_counterwall_deck_shell_more_than_cf34_pilot |

## Arm table

| Arm | Life | Score | W-L | Library-win share | Library wins | Life wins | Mean decisions |
|---|---:|---:|---:|---:|---:|---:|---:|
| A_original_size_skew | 20 | 0.812 | 13-3 | 0.846 | 11 | 2 | 272.6 |
| A_original_size_skew | 40 | 0.688 | 11-5 | 0.818 | 9 | 2 | 275.2 |
| B_pilot_swap_size_skew | 20 | 0.375 | 6-10 | 0.667 | 4 | 2 | 300.0 |
| B_pilot_swap_size_skew | 40 | 0.312 | 5-11 | 1.000 | 5 | 0 | 319.8 |
| C_equalized_40v40 | 20 | 0.375 | 6-10 | 1.000 | 6 | 0 | 257.2 |
| C_equalized_40v40 | 40 | 0.438 | 7-9 | 1.000 | 7 | 0 | 245.6 |
| D_equalized_60v60 | 20 | 0.688 | 11-5 | 0.727 | 8 | 3 | 355.0 |
| D_equalized_60v60 | 40 | 0.500 | 8-8 | 1.000 | 8 | 0 | 360.2 |
| E_same_deck_counter60_pilot | 20 | 0.562 | 9-7 | 1.000 | 9 | 0 | 411.1 |
| E_same_deck_counter60_pilot | 40 | 0.688 | 11-5 | 1.000 | 11 | 0 | 419.8 |
| F_same_deck_overlord40_pilot | 20 | 0.688 | 11-5 | 0.727 | 8 | 3 | 215.4 |
| F_same_deck_overlord40_pilot | 40 | 0.438 | 7-9 | 0.857 | 6 | 1 | 215.8 |

## Read

The strongest directional result is that the original edge does **not** follow the cf34 pilot under the pilot swap.

At life 20:

```text
original size-skew score: 0.8125
pilot-swap score:        0.3750
40v40 score:             0.3750
60v60 score:             0.6875
```

At life 40:

```text
original size-skew score: 0.6875
pilot-swap score:        0.3125
40v40 score:             0.4375
60v60 score:             0.5000
```

That pattern points away from a pure `cf34` pilot-skill story.  The edge appears to follow the counter-wall shell and/or the 60-card endurance buffer more than the pilot.  The library-out mechanism remains central: most target wins in the positive cells are opponent library-out wins.

## Limits

Each arm/life cell has 16 games.  This is sufficient as a risk-reduction decomposition pass, not sufficient as a final claim.  The next high-value move is a seed-disjoint focused confirmation of only the explanatory cells that mattered most: original size-skew, pilot swap, 40v40, and 60v60.

## Files

```text
src/muc5/terminal_mechanisms.py
src/muc5/terminal_decomposition.py
tests/test_rev0058_decomposition_mechanisms.py
scripts/run_rev0058_decomposition.py
data/rev0058_decomposition_summary.json
data/rev0058_decomposition_games.csv
data/rev0058_decomposition_arm_summary.csv
data/rev0058_decomposition_mechanisms.csv
data/rev0058_decomposition_comparisons.csv
data/rev0058_decomposition_cpp_transition_sample.csv
```
