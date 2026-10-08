# nativeboundaryfold audit/refactor

`nativeboundaryfold.py` pins rev0081 through source, tests, docs, public pointers, fold map, fold registry, surface ledger, and the rev0080 `importsettlementfold` predecessor.

This is also an audit/refactor move: the cube now has a first-class language boundary.  Future native work should not be scattered as miscellaneous performance experiments.  It must declare whether it is a pure leaf, a vetted native binding, a held parser candidate, or a rejected rewrite.
