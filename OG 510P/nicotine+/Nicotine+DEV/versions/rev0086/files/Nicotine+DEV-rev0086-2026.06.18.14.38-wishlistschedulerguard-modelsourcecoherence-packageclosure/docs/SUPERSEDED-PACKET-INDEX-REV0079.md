# Superseded packet index — rev0079

The following remain valuable evidence but are not current decision authority:

```text
docs/SEARCH-AGAIN-EPOCH-01-CURRENT-DISPOSITION-REV0078.md
  superseded by the rev0079 output-ownership and complete-fan-out boundary

docs/SEARCH-EPOCH-TRANSACTION-CONTRACT-REV0078.md
  its acknowledgement-before-serialization sketch is too weak because current
  packing and outgoing helpers can fail silently

docs/SEARCH-EPOCH-OWNER-MAP-REV0078.md
  retained as the current identity-owner baseline, but read with rev0079
  acknowledgement semantics
tools/probe_rev0078_search_epoch.py
  retained as the one-phase/queue-acceptance evidence baseline
maintainer_artifacts/search-epoch-01/search_epoch_model.py
  retained as the one-phase countermodel; not the current acknowledgement model
```

Current open-first authority is declared in `data/current_revision_contract.json`.
