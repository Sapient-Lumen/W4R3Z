# Simulator status after rev0048

The simulator is still Python-authoritative, with C++ used as a parity-checked shadow/acceleration path.

rev0048 does not change game rules. It changes evaluation discipline:

```text
max_decisions = 380  -> useful for branch/ranker smoke tests
max_decisions = 900  -> cleaner terminal payoff table for the rev0047 panel
```

This matters because some counter/control shells are slow. A low ceiling can convert real slow games into draw-half rows. Since draw-half is reporting-only, high-truncation panels should not drive policy promotion or training labels.

The rev0048 high-ceiling rerun produced:

```text
144 terminal games
0 truncations
43,088 C++-checked transitions
0 C++ mismatches
```

The simulator is therefore strong enough for this particular terminal-clean smoke panel. It is still not a basis for high-confidence pairwise MUC claims because repetitions are small.
