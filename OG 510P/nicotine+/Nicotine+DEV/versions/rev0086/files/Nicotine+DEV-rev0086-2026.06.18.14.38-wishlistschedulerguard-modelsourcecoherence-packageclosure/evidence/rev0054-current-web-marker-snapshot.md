# Current-web marker snapshot evidence — rev0054

This evidence file records the web-visible marker reconciliation performed in rev0054. It is intentionally a classifier, not a replacement for a clean checkout and regression rerun.

## Summary

- Web branches observed: `master`, `3.3.x`.
- Packet rows: 14.
- Selected marker observations: 2 present / 34 missing across 36 marker checks.
- Only PB-01 has a partial textual overlap (`keeping established primary connection`), and rev0054 classifies it as non-sufficient because it belongs to legacy fallback behavior rather than the selected replacement/promotion guard.

## Packet disposition

### U-123 — download transfer-token active-owner collision

- Classification: selected marker set absent in current web snapshot.
- Web observation: Transfers still assign active_users[username][token] directly and deactivate by deleting the active_users slot; downloads.py did not expose the selected duplicate-request rejection marker.
- Remaining gate: fresh checkout plus U-123 fixed-regression rerun still required before external filing.

### PB-01 — peer primary-election replacement/promotion guard

- Classification: partial textual overlap only; selected invariant not classified native from web markers.
- Web observation: The current web view still shows _replace_existing_connection(init). A pre-existing indirect-fallback log contains the phrase keeping established primary connection, but the selected rejection/guard markers were not visible.
- Remaining gate: fresh checkout plus PB-01 fixed-regression rerun still required before external filing.

### SEARCH-RESP-01A — direct user-search FileSearchResponse source binding

- Classification: selected marker set absent in current web snapshot.
- Web observation: The current web view of _file_search_response performs token/search lookup and ignore checks, but the selected expected_users source-binding markers were not visible.
- Remaining gate: fresh checkout plus SEARCH-RESP-01A fixed-regression rerun still required before external filing.

### SEARCH-RESP-01B-BUDDY — buddy-mode request-time source snapshot

- Classification: selected marker set absent in current web snapshot.
- Web observation: The current web view still sends buddy UserSearch requests from core.buddies.users; selected request-time tuple snapshot and response gate markers were not visible.
- Remaining gate: fresh checkout plus SEARCH-RESP-01B-BUDDY fixed-regression rerun still required before external filing.

### SEARCH-RESP-01C-ROOM — room-mode membership-snapshot source binding when available

- Classification: selected marker set absent in current web snapshot.
- Web observation: The current web view exposes room search request handling, but the selected room_obj/member-snapshot source gate markers were not visible.
- Remaining gate: fresh checkout plus SEARCH-RESP-01C-ROOM fixed-regression rerun still required before external filing.

### SEARCH-RESP-PARSE-BUDGET-A — compressed FileSearchResponse username-prefix cap

- Classification: selected marker set absent in current web snapshot.
- Web observation: The selected MAX_SEARCH_RESPONSE_USERNAME_LENGTH and username_len cap markers were not visible in current master or 3.3.x raw slskmessages.py views.
- Remaining gate: fresh checkout plus SEARCH-RESP-PARSE-BUDGET-A fixed-regression rerun still required before external filing.

### SEARCH-RESP-PARSE-BUDGET-B — accepted public/private FileSearchResponse result-count budget

- Classification: selected marker set absent in current web snapshot.
- Web observation: The selected MAX_SEARCH_RESPONSE_RESULT_COUNT and accepted_result_count cap markers were not visible in current master or 3.3.x raw slskmessages.py views.
- Remaining gate: fresh checkout plus SEARCH-RESP-PARSE-BUDGET-B fixed-regression rerun still required before external filing.

## Limits

- Raw web views do not pin a complete checkout commit, cannot run tests, and can lag or render differently from git/tarball sources.
- Final external filing remains blocked until the current-source checkout and seven fixed-regression gates are completed.
