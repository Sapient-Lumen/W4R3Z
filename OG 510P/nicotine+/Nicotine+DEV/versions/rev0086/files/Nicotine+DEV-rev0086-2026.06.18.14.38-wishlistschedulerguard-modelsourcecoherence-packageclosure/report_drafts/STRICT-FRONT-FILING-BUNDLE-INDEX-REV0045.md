# Strict/front filing bundle index — rev0045

This is a report-draft companion to `docs/STRICT-PACKET-FILING-BUNDLE-INDEX-REV0045.md`.

Recommended filing sequence:

```text
1. U-123
2. PB-01
3. SEARCH-RESP-01A
4. SEARCH-RESP-01B-BUDDY
5. SEARCH-RESP-01C-ROOM
6. SEARCH-RESP-PARSE-BUDGET-A
7. SEARCH-RESP-PARSE-BUDGET-B
```

Do not file the five search-response packets as one undifferentiated issue. The source-admission series and parser-budget series have different compatibility arguments and different likely maintainers/review paths.

Use `data/rev0045_strict_packet_index.csv` as the attachment checklist.
