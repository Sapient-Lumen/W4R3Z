# rev0072 — summaryreceipt-importarchive-lineageprune

rev0072 extends the redacted closure-handoff chain after rev0071:

```text
closure handoff -> handoff receipt -> handoff import -> summary lineage
  -> summary receipt -> import archive -> lineage prune guard
```

The strongest sentence for this revision is:

> A redacted summary is not received, archived, or prunable merely because lineage exists; each step must preserve contradiction/import/handoff memory at the same exact boundary.

The implementation remains a no-network Python DHT design cube.  It adds deterministic local-pressure surfaces for summary receipt, import archival, and pruning of summary-lineage working state.

## New risk-first surfaces

- `summaryreceipt.py` makes summary ACK/refusal memory explicit.  A refusal becomes watch pressure, not success.
- `importarchive.py` archives accepted summary receipt while carrying summary-lineage, handoff-import, handoff-receipt, closure-handoff, and contradiction memory.
- `lineageprune.py` makes pruning its own permission.  It can compact soft working state, but cannot erase contradiction/import/archive memory.
- `summaryreceiptfold.py` is the current audit/refactor fold and preserves rev0071 `handoffreceiptfold` as predecessor history.

## Nonclaims

No live I2P/SAM transport.  No production DHT.  No production handoff/import/archive/prune protocol.  No global reputation.  No mutable-head consensus.  No private retrieval guarantee.  No Sybil/anonymity guarantee.  No Nicotine+ patch.
