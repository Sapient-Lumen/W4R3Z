# rev0080 — importsettlement-archive-retentionseal

This revision goes one seam past rev0079:

```text
summary export receipt
+ summary import gate
+ export retention audit
    ≠ locally settled import
    ≠ restart-sticky import archive
    ≠ retention-sealed cleanup boundary
```

The riskiest guess in this turn is that **import permission is not imported state**. A recipient may acknowledge a redacted export, a local gate may permit import, and retention audit may say the evidence is preserved, but none of those facts should mutate sticky local state alone.

New active surfaces:

```text
src/i2p_dht_lab/summaryimportsettlement.py
src/i2p_dht_lab/importarchiveledger.py
src/i2p_dht_lab/importretentionseal.py
src/i2p_dht_lab/importsettlementfold.py
tests/test_rev0080_importsettlement_archive_retentionseal.py
```

Strongest sentence:

```text
Import-gated redacted evidence is not settled, archived, or retention-safe until settlement, archive, and seal each preserve redaction and contradiction memory at the exact boundary.
```

The audit/refactor lane moves the current fold head from `summaryexportreceiptfold` to `importsettlementfold`, while preserving rev0079 as predecessor history.
