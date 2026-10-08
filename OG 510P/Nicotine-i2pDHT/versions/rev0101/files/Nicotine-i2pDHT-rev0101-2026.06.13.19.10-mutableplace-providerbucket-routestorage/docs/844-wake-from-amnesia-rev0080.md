# Wake from amnesia — rev0080

Start with `docs/838-rev0080-importsettlement-archive-retentionseal.md`.

Current path:

```text
summaryexportreceipt
  -> summaryimportgate
  -> exportretentionaudit
  -> summaryimportsettlement
  -> importarchiveledger
  -> importretentionseal
```

The invariant is: import permission is not imported state, and imported state is not safe to archive or clean up unless redaction and contradiction memory survive each exact-boundary join.
