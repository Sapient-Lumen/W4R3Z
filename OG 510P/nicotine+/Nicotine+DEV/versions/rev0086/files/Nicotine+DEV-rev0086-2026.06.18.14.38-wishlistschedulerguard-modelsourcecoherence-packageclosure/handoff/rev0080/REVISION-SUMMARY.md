# rev0080 revision summary

Rev0080 changes the diagnosis of `SEARCH-AGAIN-EPOCH-01` and compacts its active evidence.

The current same-token Search Again command is confirmed nonproductive once a page reaches `max_displayed_results`: it re-allows and resends the token, but the first response immediately retires that token because the stored-result count was not reset. No new row can be added. Repeated buddy/user clicks can therefore create bounded local fan-out with zero possible display benefit.

Git-history provenance establishes a cross-commit interaction. The May 2025 feature snapshot contained both same-token Search Again and a manual **Clear All Results** reset. The January 2026 wishlist overhaul removed the reset while leaving Search Again intact.

The cube also corrects its own architecture framing. Rev0078–rev0079 modeled a valid but optional failure-atomic in-place refresh. A fresh-token replacement page can instead inherit ordinary best-effort new-search semantics and does not require a network-applied acknowledgement. No patch is selected because tab/undo state, plugin events, and wishlist identity still require native integration.

## Validation

```text
research/model/source tests:  17/17 pass
source invariants:            19/19 pass
source-history checks:        36/36 pass
history claims:               15
compile checks:                8/8 pass
upstream units:               60 passed, 1 skipped
selected patch:               none
```

## Cube refactor

```text
former active in-place packet: 13 files / 2,011 lines / 73,774 bytes
new active repeat packet:       7 files /   382 lines / 15,693 bytes
current-authority reduction:    6 files / 1,629 lines / 58,081 bytes
```

The prior packet remains preserved as historical evidence. `data/current_source_history_contract.json` and `tools/audit_current_source_history.py` now make cross-commit provenance executable.

The provenance tool was self-audited before packaging: repeated full `git show` logs (~682 KiB) were replaced by a 2,886-byte command/digest ledger, leaving historical source external.
