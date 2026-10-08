# Claim card update — rev0058 cf34 decomposition

## Claim under examination

Original wording from rev0056/rev0057:

```text
cf34_counter_wall beats pub_threat_overlord in both life cells, mostly by opponent library-out.
```

## New evidence

rev0058 tests whether that edge follows the pilot or the shell.

| Life | Original | Pilot swap | 40v40 | 60v60 | same counter60 pilot | same overlord40 pilot | Provisional read |
|---:|---:|---:|---:|---:|---:|---:|---|
| 20 | 0.812 | 0.375 | 0.375 | 0.688 | 0.562 | 0.688 | edge_follows_counterwall_deck_shell_more_than_cf34_pilot |
| 40 | 0.688 | 0.312 | 0.438 | 0.500 | 0.688 | 0.438 | edge_follows_counterwall_deck_shell_more_than_cf34_pilot |

## Status

The claim remains real as an observed local matchup result, but the mechanism label should change again:

```text
60-card counter-wall/endurance shell beats 40-card threat shell largely through library-out pressure.
```

Do **not** describe this as mainly a cf34 pilot edge.  In the pilot-swap arm, the cf34 pilot moved onto the 40-card Overlord shell and lost in both life cells.

## Needed before stronger language

Run a seed-disjoint confirmation on four focused arms:

```text
A_original_size_skew
B_pilot_swap_size_skew
C_equalized_40v40
D_equalized_60v60
```

Promote only if the original remains positive, the pilot swap remains negative or weak, and the equalized-size arms explain which part of the shell/size effect is stable.
