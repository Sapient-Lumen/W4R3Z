# rev0024 simulator notes

No new Magic card mechanics were added in rev0024.

The simulator change is pregame-facing:

```text
MulliganObservation now includes starting_life and own deck_counts.
```

The gameplay simulator remains the same five-card MUC-5 referee:

```text
Island
Counterspell
Force of Will
Jace, the Mind Sculptor
Overlord of the Floodpits
```

The learned mulligan ranker uses only its own opening hand, own deck composition, mulligan count, bottom count remaining, and public starting life. It does not see the opponent's hand or library.

C++ status in this revision:

```text
no new C++ kernel
new learned-mulligan traffic passed the existing batched C++ recorded-trace checker
```
