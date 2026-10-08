# summaryreceiptfold audit/refactor

`summaryreceiptfold.py` is the rev0072 current-path fold.  It checks:

```text
summaryreceipt.py
importarchive.py
lineageprune.py
summaryreceiptfold.py
tests/test_rev0072_summaryreceipt_importarchive_lineageprune.py
docs/758..762
foldmap
foldregistry
surfaceledger
rev0071 handoffreceiptfold predecessor
```

This audit/refactor pass keeps the new redacted-summary surfaces navigable without deleting older wake-from-amnesia history.
