# Strict packet filing bundle index — rev0045

This file is the maintainer-facing navigation index for the seven production-gated packets. It is not a new disclosure text; it tells the next reviewer which packet to read first, which tests/patches belong together, and which packets should not be merged prematurely.

## Recommended order

1. **U-123** — transfer-token active-owner collision. Independent and concrete. File first if filing only one packet.
2. **PB-01** — peer primary-election and secondary-promotion guard. Compatibility-sensitive but well bounded.
3. **SEARCH-RESP-01A** — direct user-search response source binding. Lowest-risk search source gate.
4. **SEARCH-RESP-01B-BUDDY** — buddy request-time source snapshot. Builds naturally after 01A.
5. **SEARCH-RESP-01C-ROOM** — room source snapshot when a local membership snapshot exists. Keep after 01A/01B because server-mediated room behavior needs the compatibility carve-out.
6. **SEARCH-RESP-PARSE-BUDGET-A** — pre-token compressed username-prefix cap.
7. **SEARCH-RESP-PARSE-BUDGET-B** — accepted public/private result-row count budget.

## Packet paths

See `data/rev0045_strict_packet_index.csv` for the full report/patch/test/evidence path map.

## Why the search packets remain split

The five search-response packets share protocol context but not the same invariant:

```text
01A: direct user source admission
01B: buddy request-time source snapshot
01C: room snapshot admission only when a local snapshot exists
BUDGET-A: pre-token compressed prefix bound
BUDGET-B: accepted row-count materialization bound
```

Merging them would obscure compatibility decisions. The source-admission rows can be reviewed as a small series; the parser-budget rows can be reviewed as a separate parser-boundary series.

## Filing hygiene

Each report draft intentionally avoids claims of remote code execution, credential disclosure, or arbitrary file access. The evidence supports bounded availability/state-integrity/parser-budget impacts. Keep that boundary unless a maintainer asks for broader threat modeling.
