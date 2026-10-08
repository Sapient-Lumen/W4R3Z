# rev0084 — parserhold-sanitizerplan-nativebudget

rev0084 continues the GCC-native thread by adding three brakes before the cube grows more native code.

The strongest rule is: **native code remains a narrow optimization surface, not a second authority.**

New surfaces:

- `parserhold.py` keeps hostile-byte parsing Python-owned.
- `sanitizerplan.py` requires sanitizer/fuzz posture before new native leaf classes are considered.
- `nativebudget.py` budgets native optimization by component, call site, input size, fallback, and forbidden semantic surface.
- `nativebudgetfold.py` audits the current path and preserves the rev0083 native dispatch predecessor.

This revision deliberately does not add a native parser, crypto primitive, transport session manager, or mutable-record authority. It treats those as quarantine surfaces until much later evidence exists.
