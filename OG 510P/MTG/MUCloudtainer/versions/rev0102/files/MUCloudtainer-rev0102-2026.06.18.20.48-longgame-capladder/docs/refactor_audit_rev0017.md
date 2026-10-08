# rev0017 refactor and audit notes

## Refactor

rev0017 keeps C++ seams separated by purpose:

```text
src/muc5/cpp_accel.py       dense numeric deck-probe C++ bridge
src/muc5/cpp_legal.py       legal-menu C++ bridge
src/muc5/cpp_transition.py  one-action transition C++ bridge
```

This avoids a single opaque `cpp.py` that mixes unrelated contracts.

The new transition bridge uses explicit flat records rather than handing C++ a Python object or arbitrary JSON. The TSV schema is verbose but stable, fast enough, and easy to diff.

## Audit additions

`scripts/audit_cube.py` now checks:

```text
C++ transition microkernel builds with local g++
rev0017 transition diff has 0 mismatches
transition diff has both directed and sampled cases
meta-rank payoff table passed promotion/statistical gates
meta-rank mass sums to 1.0
required rev0017 files exist
```

## Known caveat

The transition microkernel is intentionally incomplete. Missing families are listed in `docs/cpp_transition_micro_rev0017.md`. Treat it as a bridge, not a replacement referee.
