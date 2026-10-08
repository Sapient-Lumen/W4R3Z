# Packet disposition ledger — rev0083

Machine authority: `data/current_packet_dispositions.json`.

```text
U-123                    closed research disposition
PB-01A/U-168             open protocol-hardening research
PB-01B/U-176             retired as defect on current evidence
SEARCH-RESP-01A/U-163A   open defense-in-depth research
SEARCH-RESP-01B/U-163B   open request-epoch design research
SEARCH-AGAIN-SELF-01     closed low-severity correctness disposition
SEARCH-AGAIN-EPOCH-01A   non-wishlist modes; open native-UI validation
SEARCH-AGAIN-EPOCH-01B   persistent wishlist; open product-policy research
SEARCH-AGAIN-EPOCH-01C   manual wishlist hybrid; open policy research
```

Rev0083 corrects the rev0082 two-way split. Manual wishlist pages are normal
core requests with wishlist GUI behavior, so they require their own authority
rather than being mislabeled as either ordinary or persistent wishlist state.
No epoch packet selects a patch.
