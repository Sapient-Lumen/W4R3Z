# rev0043 public-overlap notes — SEARCH-RESP-01C-ROOM

## Captured sources

- https://nicotine-plus.org/doc/SLSKPROTOCOL.html
  - Protocol context: `RoomSearch` is a server message carrying room, token, and search query; room users receive the request as `FileSearch`; `FileSearchResponse` uses the token from the original `FileSearch`, `UserSearch`, or `RoomSearch`.
- https://github.com/nicotine-plus/nicotine-plus/issues/3326
  - Search lifecycle adjacency: public issue discussing search refresh/token behavior. Not a room-source duplicate.
- https://github.com/nicotine-plus/nicotine-plus/issues/3624
  - Search/load/performance adjacency. Not a room-source duplicate.
- https://github.com/nicotine-plus/nicotine-plus/releases and https://nicotine-plus.org/NEWS.html
  - Public release-note adjacency for search-result performance/loading improvements. Not a room-source duplicate.

## Classification

Conservative classification: protocol-supported, search-result-adjacent, **no exact public duplicate captured** for the rev0043 narrow shape:

```text
RoomSearch response admission should bind to a request-time local joined-room membership snapshot when one exists, while preserving broad-source compatibility when no authoritative local room snapshot exists.
```
