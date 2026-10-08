# Source trace — SEARCH-RESP-PARSE-BUDGET-B rev0042

## `pynicotine/slskmessages.py`

`FileSearchResponse` is the peer-message parser for search results.

- `github-tag-3.3.10`: class begins around line 3234. `parse_network_message()` reads username length and token, rejects invalid tokens, then decompresses the remaining accepted body and calls `_parse_remaining_network_message()`. `_parse_result_list()` reads `nfiles` and appends one Python tuple per advertised row.
- `github-branch-3.3.x`: class begins around line 3262. The same shape is present, with a 128 MiB maximum decompressed size around line 3310. The count-to-row materialization loop remains uncapped.
- `github-branch-master`: class begins around line 3435. The same shape is present with the newer `msg_content`/`allowed_responses` handler style and 128 MiB decompression cap.

## UI/config policy is later than parser materialization

Archived defaults include:

```text
config.py: maxresults = 300
config.py: max_displayed_results = 2500
config.py: private_search_results = False
```

The GTK search view consults `max_displayed_results` and `private_search_results` after the parser has already constructed `msg.list` and `msg.privatelist`. Therefore rev0042 treats UI display policy as adjacent context, not as the parser-boundary fix.
