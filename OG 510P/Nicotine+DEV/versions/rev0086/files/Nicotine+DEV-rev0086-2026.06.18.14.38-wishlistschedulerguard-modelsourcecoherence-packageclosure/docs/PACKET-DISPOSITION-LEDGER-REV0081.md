# Packet disposition ledger — rev0081

Machine authority: `data/current_packet_dispositions.json`.

```text
U-123                    closed research disposition
PB-01A/U-168             open protocol-hardening research
PB-01B/U-176             retired as defect on current evidence
SEARCH-RESP-01A/U-163A   open defense-in-depth research
SEARCH-RESP-01B/U-163B   open request-epoch design research
SEARCH-AGAIN-SELF-01     closed low-severity correctness disposition
SEARCH-AGAIN-EPOCH-01    open wishlist-policy/native-UI validation; no selected patch
```

Rev0081 changes only `SEARCH-AGAIN-EPOCH-01`. A same-page fresh-token rekey is mechanically viable for ordinary searches on the executable proxy, so page replacement is no longer the presumed minimum. Wishlist semantics and native GTK integration remain open.
