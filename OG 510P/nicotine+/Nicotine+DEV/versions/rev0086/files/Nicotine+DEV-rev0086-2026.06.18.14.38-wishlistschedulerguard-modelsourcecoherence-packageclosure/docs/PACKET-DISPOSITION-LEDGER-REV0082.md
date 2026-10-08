# Packet disposition ledger — rev0082

Machine authority: `data/current_packet_dispositions.json`.

```text
U-123                    closed research disposition
PB-01A/U-168             open protocol-hardening research
PB-01B/U-176             retired as defect on current evidence
SEARCH-RESP-01A/U-163A   open defense-in-depth research
SEARCH-RESP-01B/U-163B   open request-epoch design research
SEARCH-AGAIN-SELF-01     closed low-severity correctness disposition
SEARCH-AGAIN-EPOCH-01A   open native-UI validation; no selected patch
SEARCH-AGAIN-EPOCH-01B   open wishlist product-policy research; no selected patch
```

Rev0082 replaces the combined `SEARCH-AGAIN-EPOCH-01` authority with two packets. Ordinary token mechanics no longer wait on wishlist semantics, and wishlist policy cannot be changed incidentally by an ordinary rekey patch.
