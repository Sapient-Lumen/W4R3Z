# Experiment matrix — rev0058

## Completed in this revision

| Arm | Purpose | Result read |
|---|---|---|
| A_original_size_skew | Anchor the rev0056 contrast | Positive at both life totals |
| B_pilot_swap_size_skew | Test whether the edge follows the cf34 pilot | Negative at both life totals |
| C_equalized_40v40 | Remove target 60-card buffer | Negative/weak |
| D_equalized_60v60 | Remove opponent 40-card liability | Positive at life 20, neutral at life 40 |
| E_same_deck_counter60_pilot | Same counter deck, pilot-only control | cf34 pilot modestly positive |
| F_same_deck_overlord40_pilot | Same Overlord deck, pilot-only control | mixed |

## Numerical summary

| Life | Original | Pilot swap | 40v40 | 60v60 | same counter60 pilot | same overlord40 pilot | Provisional read |
|---:|---:|---:|---:|---:|---:|---:|---|
| 20 | 0.812 | 0.375 | 0.375 | 0.688 | 0.562 | 0.688 | edge_follows_counterwall_deck_shell_more_than_cf34_pilot |
| 40 | 0.688 | 0.312 | 0.438 | 0.500 | 0.688 | 0.438 | edge_follows_counterwall_deck_shell_more_than_cf34_pilot |

## Next matrix

| ID | Question | Minimal design | Stop condition |
|---|---|---|---|
| E58-A | Does the deck/shell read replicate? | seed-disjoint rerun of A-D only, more reps | A positive, B weak/negative, C/D explanatory |
| E58-B | Is 60v60 life-40 truly neutral? | add reps only to D_equalized_60v60 life 40 | interval separates from original or remains uncertain |
| E58-C | Is same-deck pilot edge real? | rerun E/F with larger cells if needed | only after A-D confirmation |
| E58-D | Is Jace activation the library-out driver? | no-Jace/low-Jace controls | after size/shell confirmation |

The key discipline: do not broaden until A-D survive a fresh seed family.
