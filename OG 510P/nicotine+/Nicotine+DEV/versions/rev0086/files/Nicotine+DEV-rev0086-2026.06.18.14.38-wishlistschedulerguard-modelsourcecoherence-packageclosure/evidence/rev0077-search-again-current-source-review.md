# rev0077 current-source review

## Visible public master

```text
head: a96406e7aa285a3fb2a3e35900686d164a22bf02
date shown by GitHub: 2026-06-15
```

Current raw `pynicotine/search.py` confirms:

```text
send_search_request(token)
  resolves self.searches[token]
  delegates user mode to _send_peer_search_request(search)

_send_peer_search_request(search)
  records self.token for the local username
  sends UserSearch(..., search.token, ...)

_process_search_request(..., token)
  requires token in _own_tokens for local-username requests
  consumes that exact incoming token
```

Current raw `pynicotine/gtkgui/search.py` confirms Search Again delegates with the page's existing token and the result page retains per-username deduplication until model clear.

## Executable proxy

```text
ref: f4e17d59783dbc48ea31d2e899a681e2dd1ed500
source: content-addressed bundled master lane
```

GitHub reports six commits and eight changed files between the proxy and visible head. Direct current-file inspection confirms the relevant flow still exists, but the executable tests are accurately attributed to the proxy rather than the visible head.
