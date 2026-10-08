# Audit-mesh refactor

The cube has many historical fold modules. They were useful while each revision had one or two surfaces. By rev0031, bespoke folds are themselves design debt: each fold can forget public pointers, docs, tests, or predecessor status.

`auditmesh.py` starts a declarative replacement. It checks the current revision's active modules, tests, docs, public surface needles, head registry needles, docs index needles, README/START_HERE revision visibility, active surface-ledger entries, and the rev0030 predecessor fold.

The first goal is not elegance. The first goal is to make wake-from-amnesia navigation fail closed when a current surface is present but unreachable.
