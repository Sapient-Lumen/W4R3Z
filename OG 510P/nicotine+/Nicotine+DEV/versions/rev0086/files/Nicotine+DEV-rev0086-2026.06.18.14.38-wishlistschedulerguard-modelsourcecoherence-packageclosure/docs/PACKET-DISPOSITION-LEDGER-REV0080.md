# Packet disposition ledger — rev0080

Machine authority: `data/current_packet_dispositions.json`.

```text
U-123                    closed research disposition
PB-01A/U-168             open protocol-hardening research
PB-01B/U-176             retired as defect on current evidence
SEARCH-RESP-01A/U-163A   open defense-in-depth research
SEARCH-RESP-01B/U-163B   open request-epoch design research
SEARCH-AGAIN-SELF-01     closed low-severity correctness disposition
SEARCH-AGAIN-EPOCH-01    open fresh-token replacement research; no selected patch
```

Rev0080 changes only the last packet's current authority. It confirms the result-cap dead end, treats the rev0078–rev0079 in-place transaction as an optional architecture branch, and makes fresh-token page replacement the next bounded experiment.

Historical filenames containing `PRODUCTION-READY`, `SELECTED-PATCH`, `FINAL`, or an earlier `CURRENT-DISPOSITION` do not override the machine ledger.
