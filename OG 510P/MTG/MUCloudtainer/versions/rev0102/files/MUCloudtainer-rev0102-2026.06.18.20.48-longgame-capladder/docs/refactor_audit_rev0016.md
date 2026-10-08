# rev0016 refactor/audit notes

## Refactor

rev0016 adds a second C++ wrapper module instead of expanding the rev0015 probe wrapper:

```text
src/muc5/cpp_accel.py   # numeric deck-probe shared library
src/muc5/cpp_legal.py   # standalone legal-menu executable bridge
```

This separation is intentional. Deck probes are dense numeric arrays. Legal menus are dynamic strings and state summaries. Forcing them into one wrapper would blur contracts.

## Audit additions

`scripts/audit_cube.py` now checks:

```text
C++ legal-menu tool builds with local g++
C++/Python legal-menu diff has 0 mismatches
legal-menu diff covers at least MAIN/RESPONSE/ATTACK
sequential race generated expected rows
sequential race statistical gate passed
rev0016 required files are present
```

## Bug class guarded

The new C++ TSV parser had to preserve empty positional fields. This matters because `pending_kind` is often empty; dropping empty fields shifts every later column and silently corrupts the legal menu. The wrapper/diff harness is the guard against this class of C++ bridge bug.
