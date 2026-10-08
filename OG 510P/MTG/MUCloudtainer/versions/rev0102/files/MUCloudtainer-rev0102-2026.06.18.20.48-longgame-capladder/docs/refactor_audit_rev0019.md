# rev0019 refactor and audit notes

## Refactor

The new code is intentionally separated from earlier C++ bridges:

```text
src/muc5/cpp_accel.py       numeric deck-probe bridge
src/muc5/cpp_legal.py       legal-menu bridge
src/muc5/cpp_transition.py  one-action transition bridge
src/muc5/cpp_trace.py       recorded-trace bridge checker
```

This avoids collapsing different trust contracts into one opaque module. A numeric probe kernel, a legal-menu enumerator, a one-action transition kernel, and a trace checker all fail differently and should remain independently auditable.

## Audit checks added

rev0019 extends `scripts/audit_cube.py` with checks for:

```text
rev0019 C++ trace summary exists
C++ trace checker saw at least 8,000 events
support rate is at least 99%
C++ mismatches are zero
Python replay errors are zero
unsupported events are only expected Jace ultimate coverage debt
required rev0019 files are present
```

## Known debt

Jace ultimate is intentionally unsupported in the C++ transition microkernel. It exiles the target library, shuffles the target hand into the target library, and therefore needs explicit RNG/shuffle transport before C++ should claim equivalence.
