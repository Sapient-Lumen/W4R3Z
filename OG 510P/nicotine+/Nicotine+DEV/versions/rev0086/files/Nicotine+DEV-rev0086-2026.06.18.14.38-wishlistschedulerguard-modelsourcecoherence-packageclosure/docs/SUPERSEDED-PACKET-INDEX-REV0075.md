# Superseded packet index — rev0075

## SEARCH-RESP-01A

| Historical artifact family | Current classification | Reason |
|---|---|---|
| `docs/SEARCH-RESP-01A-USER-SCOPE-PRODUCTION-GATE-REV0039.md` | superseded decision | guard mechanics were promoted before identity/reachability/impact proof |
| `report_drafts/SEARCH-RESP-01A-PRODUCTION-READY-MAINTAINER-REPORT-REV0039.md` | historical draft only | “production-ready” is not the current disposition |
| `report_drafts/SEARCH-RESP-01A-SELECTED-PATCH-REV0039-3.3.10.diff` and apply helper | unselected defense-in-depth experiment | filters claimed names but does not authenticate them |
| rev0045, rev0056, rev0058, and later patch-stack reruns | mechanical historical evidence | source/roundtrip success does not close missing claim rungs |
| handoff/export copies | duplicate historical exports | current ledger overrides embedded status language |

Current SEARCH-RESP-01A authority is `docs/SEARCH-RESP-01A-CURRENT-DISPOSITION-REV0075.md` plus `data/current_packet_dispositions.json`.

## PB-01 retained correction

The rev0038 PB-01 blanket primary guard and its production-ready/selected-patch derivatives remain superseded by rev0074's direct/indirect race counterexample. Current PB-01 authority remains `docs/PB01-CURRENT-DISPOSITION-REV0074.md`.
