# Next revision pointer — rev0086

Suggested next seam:

```text
rev0087 — nativeloadreceipt-callledger-selectiongc
```

Likely work:

- selection-to-loader receipt without live dynamic loading,
- per-call native/fallback ledger after selection,
- selection GC that cannot delete fallback/quarantine history,
- native branch audit cleanup if fold drift grows.
