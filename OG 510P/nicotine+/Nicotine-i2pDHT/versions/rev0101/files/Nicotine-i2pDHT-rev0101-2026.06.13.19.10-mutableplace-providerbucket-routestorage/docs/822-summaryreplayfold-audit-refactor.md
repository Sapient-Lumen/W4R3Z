# summaryreplayfold audit/refactor

`summaryreplayfold.py` pins rev0078's active path through source, tests, docs, fold map, fold registry, surface ledger, and the rev0077 `summaryackfold` predecessor.

The audit intentionally keeps historical wake-from-amnesia surfaces while making the current path explicit:

```text
summaryreplay -> ackclosure -> summaryexportfence -> summaryreplayfold
```

This fold is the audit/refactor lane for rev0078.
