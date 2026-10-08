# rev0066 simulator note

rev0066 does not change MUC-5 referee semantics, card rules, deck legality, mulligan logic, terminal scoring, replay format, or C++ transition kernels.

The substantive behavior change is limited to public profile scoring:

```text
threat_closure: avoids selected self-counter targets
counter_guard:  avoids selected self-counter targets
threat_pressure: new public threat response profile
```

The legal menu still includes Counterspell/Force actions that target your own spell.  The new gate says guarded public profiles should not select those actions accidentally.

Validation for this revision includes:

```text
C++ chosen transitions checked: 33446
C++ mismatches/skips:           0 / 0
terminal games:                 208
truncations:                    0
replay samples:                 12 / 12 passed
selected own-spell counters:    0
```
