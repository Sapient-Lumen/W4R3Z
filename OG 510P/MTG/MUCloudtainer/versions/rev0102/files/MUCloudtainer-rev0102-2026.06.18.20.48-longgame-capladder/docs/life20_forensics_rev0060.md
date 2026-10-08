# rev0060 life-20 trajectory forensics

rev0060 follows the riskiest unresolved thread from rev0059: the cumulative life-20 A/B panel favored the original counter-wall shell, but one seed-disjoint block let the pilot-swap arm spike to 0.700.  This revision does not add another doctrine layer; it reruns the cumulative life-20 A/B games and extracts compact trajectory features.

## Scope

Input rows:

```text
rev0058_decomposition A/B life 20:       32 games
rev0059_seed_disjoint A/B life 20:       40 games
rev0059_life20_pilotstress A/B life 20:  96 games
total forensic reruns:                  168 games
```

The rerun reproduced every stored winner, score, and terminal reason.  It also exposed a separate audit issue: all 168 historical terminal rows used a legacy decision count that is one greater than the number of applied decisions.  rev0060 records corrected `applied_decisions` / `decisions` and a `legacy_terminal_row_decisions` field for reproducing old artifacts.

## Main result

Cumulative life-20 A/B stays shell-favored, but the mechanism is sharper now:

```text
A_original_size_skew:     84 games, score 0.7619
B_pilot_swap_size_skew:   84 games, score 0.4167
A-B score delta:          +0.3452
```

The strongest explanatory feature is not ordinary damage pressure.  It is the final library buffer:

```text
A mean target library buffer final:   +21.65 cards
B mean target library buffer final:   -14.38 cards
A-B library-buffer delta:             +36.04 cards
```

In A, the target is the 60-card counter-wall/Jace shell and usually survives with a large library cushion while the 40-card opponent decks out.  In B, the target is the 40-card Overlord shell; even when it wins some games, its average final library posture is poor.

## What explains the rev0059 seed-disjoint contradiction?

The seed-disjoint B block was not a clean pilot-skill refutation.  It was a small-block sample where the 40-card Overlord target converted more wins than usual despite still carrying a negative library-buffer profile:

```text
B by source block:
rev0058_decomposition:        score 0.375, mean target library buffer -15.56
rev0059_seed_disjoint:        score 0.700, mean target library buffer -11.70
rev0059_life20_pilotstress:   score 0.3125, mean target library buffer -15.10
```

The spike is real in that block, but the forensics say it is not because the B target has become an endurance deck.  B wins split between slow opponent deck-outs and faster life-total wins:

```text
B target wins by opponent library-out: 24
B target wins by opponent life-total:  11
B target losses by self-deck:          47
B target losses by own life total:      2
```

The seed-disjoint B spike therefore looks like a mixture of seed-sensitive Overlord pressure and opponent self-draw/Jace churn, not a stable reversal of the shell interpretation.

## Action-level deltas

A versus B, target-perspective means:

```text
score:                         +0.3452
final library buffer:          +36.04 cards
target Jace zero activations:   +4.77
target Counterspells cast:      +3.14
opponent Counterspells cast:    -4.79
target face attackers:          -0.56
opponent face attackers:        +0.71
```

Interpretation: A wins as a counter/Jace endurance shell, not as a proactive face-pressure shell.  B target wins are more likely to involve Overlord pressure or the opponent over-drawing; B target losses are overwhelmingly self-decking.

## What changed in the belief state

Previous working statement:

> The edge mostly follows the counter-wall/endurance shell, but life 20 has seed-sensitive pilot-swap behavior.

rev0060 refinement:

> At life 20, the cumulative A/B edge still follows the 60-card counter-wall/Jace endurance shell.  The pilot-swap spike was real but brittle: it occurred with a still-negative library-buffer profile and did not survive the stress block.  B can win through pressure or opponent over-draw, but its dominant failure mode is self-decking.

## Next highest-value experiment

Do not run another broad registry panel yet.  The next experiment should target two concrete knobs:

```text
1. no-Jace-zero / low-Brainstorm ablation on A and B
2. Overlord-pressure controlled B runs that hold opponent Jace churn constant
```

Those two should separate “library buffer from deck size” from “library churn from Jace zero.”
