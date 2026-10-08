# rev0040 hybrid-selector smoke results

Command:

```bash
PYTHONPATH=. python scripts/run_rev0040_hybrid_selector_compare.py
```

Archived summary:

```text
16 behavior games
72 behavior decisions
35 choice frames seen
16 frames with public-policy disagreement
16 sampled situations
55 union candidate actions
110 branch games
0 branch truncations
28,254 C++-checked branch transitions
0 C++ skipped transitions
0 C++ mismatches
10 union-decisive situations
```

Selector comparison:

```text
hybrid hits union-best rate:      1.000
unscreened hits union-best rate:  1.000
screened hits union-best rate:    1.000
screen-vote hits union-best rate: 0.500
behavior hits union-best rate:    0.500
```

Interpretation:

```text
hybrid did not beat unscreened or screened in this smoke panel.
It also did not lose to either.
```

This is useful but not spectacular. In the sampled situations, a branch budget of four was usually large enough that all selector variants retained at least one union-best action. The result suggests the next useful stress test is not a fancier model; it is more high-action, high-margin frames where branch budget actually binds.

Important caveat: this revision promotes no new policy. It is a label-selector audit.
