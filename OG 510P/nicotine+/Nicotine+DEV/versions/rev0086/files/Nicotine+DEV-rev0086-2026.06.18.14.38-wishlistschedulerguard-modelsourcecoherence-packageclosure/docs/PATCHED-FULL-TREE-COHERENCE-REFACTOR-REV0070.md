# Patched full-tree coherence refactor — rev0070

rev0070 adds one narrow evidence layer and keeps it separate from earlier layers.

| Layer | Scope | Status |
|---|---|---|
| rev0069 touched-file AST/static gate | five strict/front edited files | retained |
| rev0070 patched full-tree compile gate | every `.py` file in each patched archived source lane | added |
| rev0068 semantic/minimality | semantic drift and marker contracts for split patches | retained |
| rev0066 hunk/preimage binding | patch hunks against archived source preimages | retained |
| rev0067 fixture contract | clean-room regression fixture lineage | retained |
| rev0065 Git/source provenance | uploaded source lane provenance | retained |
| rev0054 current-web marker snapshot | public-web marker evidence only | retained |
| fresh current checkout proof | live-current filing proof | still pending |

## Refactor decision

Do not merge rev0070 into the current-web or fresh-checkout layers. rev0070 is valuable because it checks the selected archived patch stack across the whole Python tree, but it is still bounded by the uploaded archived source bundle.

## Strict/front packet state

No strict/front packet changes state in this revision. The seven production-gated packets remain:

```text
U-123
PB-01
SEARCH-RESP-01A
SEARCH-RESP-01B-BUDDY
SEARCH-RESP-01C-ROOM
SEARCH-RESP-PARSE-BUDGET-A
SEARCH-RESP-PARSE-BUDGET-B
```
