# rev0029 simulator notes

No card rules were changed in rev0029.

The simulator work is about training/evaluation seams:

```text
mulligan_counterfactual.py  -> first-look branch-value mulligan policy
nochoice_segments.py        -> forced-action run measurement
```

The engine remains Python-authoritative. C++ remains a shadow parity layer for this revision's new payoff/replay traffic.

rev0029 generated:

```text
432 counterfactual-mulligan payoff games
8 replay traces
2,206 C++-checked transition events
24 no-choice segment audit games
```

All C++ trace checks passed with zero skipped events and zero mismatches.
