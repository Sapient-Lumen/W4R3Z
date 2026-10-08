# nativeshadowfold audit/refactor

`nativeshadowfold.py` pins rev0094 through source, tests, docs, public pointers, fold map, fold registry, active surface ledger, native fold spine, and the rev0093 `nativeloadloopfold` predecessor.

The refactor move in this revision is extending `nativefoldspine.py` so the GCC/native line remains visible from rev0081 through rev0094 as one branch rather than scattered fold modules.
