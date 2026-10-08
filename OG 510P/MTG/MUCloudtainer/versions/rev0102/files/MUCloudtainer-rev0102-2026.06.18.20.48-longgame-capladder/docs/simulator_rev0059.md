# Simulator note — rev0059

rev0059 does not change gameplay semantics.

The Python simulator remains the semantic authority.  C++ remains a chosen-transition and replay-trace parity shadow.  New code is analytical/refactor code around decomposition comparisons and revision artifact auditing.

Validation evidence:

```text
seed-disjoint A-D terminal games: 160 / 160
life-20 A/B stress terminal games: 96 / 96
combined new terminal games: 256 / 256
truncations: 0
C++ chosen-transition mismatches: 0
C++ trace mismatches: 0
replay samples: 20 / 20 passed
```
