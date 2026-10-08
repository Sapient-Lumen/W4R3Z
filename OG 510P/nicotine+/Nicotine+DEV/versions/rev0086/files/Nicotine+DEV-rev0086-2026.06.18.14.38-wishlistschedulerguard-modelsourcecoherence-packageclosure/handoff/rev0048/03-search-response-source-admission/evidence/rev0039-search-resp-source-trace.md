# rev0039 SEARCH-RESP-01A source trace

## 3.3.10 / 3.3.x

- `pynicotine/search.py` defines `SearchRequest` with `mode`, `room`, and `users` fields.
- `Search.add_search()` stores each outgoing search under its token and records the requested user list for `mode="user"` searches.
- `Search._file_search_response()` checks the token and search object, then reads `username = msg.username`, but the archived handler proceeds to ignore/IP filtering without comparing `username` against `search.users`.
- `pynicotine/slskmessages.py::FileSearchResponse.parse_network_message()` decompresses enough of the peer payload to read the token and then parses accepted result lists.

## master

- `Search.add_allowed_token()` moved token-admission to the network thread with `AddAllowedResponse(FileSearchResponse, token)`.
- `slskproto._unpack_network_message()` injects `username=conn.init.target_user` and an allowed-response set into the peer message before parsing.
- `Search._file_search_response()` rejects parse-rejected messages and missing searches, handles wishlist ignore state, and network-filter checks, but the archived handler does not compare `msg.username` to `search.users` for `mode="user"`.

## Protocol context

The public protocol documentation says `UserSearch` sends a specific username, token, and query, and the recipient receives the request as a `FileSearch` message. The same documentation says `FileSearchResponse` uses the token from the original `FileSearch`, `UserSearch`, or `RoomSearch` message. That makes direct user-search source binding a local admission invariant, while room/global modes require separate compatibility treatment.
