# Packet disposition ledger — rev0079

Machine authority: `data/current_packet_dispositions.json`.

```text
U-123                    closed research disposition
PB-01A/U-168             open protocol-hardening research
PB-01B/U-176             retired as defect on current evidence
SEARCH-RESP-01A/U-163A   open defense-in-depth research
SEARCH-RESP-01B/U-163B   open request-epoch design research
SEARCH-AGAIN-SELF-01     closed low-severity correctness disposition
SEARCH-AGAIN-EPOCH-01    open public design research; no selected patch
```

Rev0079 changes only the last packet's current authority. It replaces “acknowledge before request serialization” with the stricter requirement that the complete fan-out be prepacked and staged in network-owned output state before a matching local acknowledgement.

Historical files do not regain authority merely because they contain labels such as `PRODUCTION-READY`, `SELECTED-PATCH`, or `FINAL`.
