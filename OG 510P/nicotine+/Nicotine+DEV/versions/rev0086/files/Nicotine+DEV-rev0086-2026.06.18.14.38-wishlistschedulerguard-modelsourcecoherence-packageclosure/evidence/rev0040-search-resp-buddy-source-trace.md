# rev0040 source trace — SEARCH-RESP-01B-BUDDY

## github-tag-3.3.10 and github-branch-3.3.x

`pynicotine/search.py` has the same relevant shape on both lanes:

```text
SearchRequest.__slots__ includes users.
Search.process_search_term(mode="buddies") calls outgoing_buddy_search_event(search_term) but leaves users unset.
Search.do_search() creates SearchRequest before dispatch; for mode="buddies" it calls do_buddies_search(search.term_transmitted).
Search.do_buddies_search() iterates live core.buddies.users and sends UserSearch(username, self.token, text).
Search._file_search_response() checks token allowance, search existence/ignored state, and network filters, but not search.mode/source membership.
```

Relevant line anchors in the archived sources:

```text
github-tag-3.3.10:   process_search_term around 277-283, do_search around 303-336, do_buddies_search around 349-351, _file_search_response around 452-474
github-branch-3.3.x: process_search_term around 277-283, do_search around 303-336, do_buddies_search around 349-351, _file_search_response around 452-474
```

## github-branch-master

Master has a refactored search sender but the same invariant gap:

```text
SearchRequest.__slots__ includes users.
Search._process_search_term(mode="buddies") calls outgoing_buddy_search_event(search_term) but leaves users unset.
Search.do_search() stores the returned users value in _add_search().
Search.send_search_request() calls _send_buddies_search_request(search).
Search._send_buddies_search_request() iterates live core.buddies.users and sends UserSearch(username, search.token, search.term_transmitted).
Search._file_search_response() checks msg.list rejection, search existence, wishlist ignored users, and network filters, but not search.mode/source membership.
```

Relevant line anchors in the archived source:

```text
github-branch-master: _process_search_term around 478-484, do_search/send_search_request around 232-275, _send_buddies_search_request around 510-512, _file_search_response around 615-641
```

## Selected invariant

For source-bound search modes, the response source should be one of the request-time usernames bound to the token:

```text
mode="user":    search.users is the explicit requested user set
mode="buddies": search.users should become the request-time buddy snapshot
```

Room mode is deliberately not folded into this invariant because its source set is server-mediated and requires a separate membership/freshness model.
