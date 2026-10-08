# nativebudgetfold audit/refactor

`nativebudgetfold.py` pins rev0084 through source, tests, docs, public pointers, fold map, fold registry, active surface ledger, and the rev0083 `nativedispatchfold` predecessor.

The audit/refactor goal is small but important: the GCC-native line now has an explicit budget and parser hold, so future revisions can add native leaves without treating native success as protocol success.
