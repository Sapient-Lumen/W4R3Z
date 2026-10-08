# Scopefold audit/refactor

`scopefold.py` is the rev0032 current-path audit surface. It keeps the new modules, tests, docs, public pointers, head registry entries, and surface ledger entries visible.

It also preserves rev0031 `foldmap.py` as predecessor history instead of deleting it. The refactor direction is to move from many ad hoc fold modules toward declarative fold maps, while retaining wake-from-amnesia evidence for historical paths.
