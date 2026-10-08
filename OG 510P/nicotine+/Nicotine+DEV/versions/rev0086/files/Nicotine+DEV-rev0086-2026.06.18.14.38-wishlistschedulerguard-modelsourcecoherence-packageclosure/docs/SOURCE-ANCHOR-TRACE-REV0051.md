# Source-anchor trace — rev0051

Rev0051 adds a line-level archived-source trace for the seven production-gated strict/front packets. The trace was generated from the external rev0003 source bundle, not by embedding source trees into this cube.

|metric|value|
|---|---|
|packets traced|7|
|source lanes|github-tag-3.3.10; github-branch-3.3.x; github-branch-master|
|source files hashed|15|
|anchor rows|126|
|new private packets|0|

## Packet summaries

|packet|anchor ids|files|decision|
|---|---:|---|---|
|U-123|8|pynicotine/downloads.py,pynicotine/slskmessages.py,pynicotine/transfers.py|retain production-gated packet; no new private packet opened in rev0051|
|PB-01|7|pynicotine/slskmessages.py,pynicotine/slskproto.py|retain production-gated packet; no new private packet opened in rev0051|
|SEARCH-RESP-01A|6|pynicotine/search.py|retain production-gated packet; no new private packet opened in rev0051|
|SEARCH-RESP-01B-BUDDY|6|pynicotine/search.py|retain production-gated packet; no new private packet opened in rev0051|
|SEARCH-RESP-01C-ROOM|6|pynicotine/search.py|retain production-gated packet; no new private packet opened in rev0051|
|SEARCH-RESP-PARSE-BUDGET-A|4|pynicotine/slskmessages.py|retain production-gated packet; no new private packet opened in rev0051|
|SEARCH-RESP-PARSE-BUDGET-B|5|pynicotine/slskmessages.py|retain production-gated packet; no new private packet opened in rev0051|

Full line-level details are in `data/rev0051_source_anchor_trace.csv` and `handoff/rev0051/anchors/`.
