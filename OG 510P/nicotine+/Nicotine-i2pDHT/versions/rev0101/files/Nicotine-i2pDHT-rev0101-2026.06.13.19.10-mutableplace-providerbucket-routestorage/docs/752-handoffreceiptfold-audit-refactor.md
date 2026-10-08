# handoffreceiptfold audit/refactor

`handoffreceiptfold.py` is the rev0071 current-path audit.

It checks:

```text
handoffreceipt.py
handoffimport.py
summarylineage.py
handoffreceiptfold.py
tests/test_rev0071_handoffreceipt_import_summarylineage.py
docs/748 through docs/752
foldmap rev0071 entries
foldregistry rev0071 entries
surfaceledger rev0071 entries
rev0070 exporthandofffold predecessor
```

The refactor direction is to keep current-path folds declarative enough that repeated boundary work remains navigable without deleting historical wake-from-amnesia material.
