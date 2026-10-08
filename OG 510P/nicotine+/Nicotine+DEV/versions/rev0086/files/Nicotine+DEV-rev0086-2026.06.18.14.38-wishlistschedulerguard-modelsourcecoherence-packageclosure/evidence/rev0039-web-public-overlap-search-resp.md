# rev0039 public-overlap notes — SEARCH-RESP-01A

## Captured public basis

- Nicotine+'s public Soulseek protocol documentation describes `UserSearch` as a request to search a specific user's shares. Its data order is username, token, and search query, and the recipient receives the request as a `FileSearch` message.
- The same documentation describes `RoomSearch` as a request to search users in a room and `FileSearchResponse` as using the token from the original `FileSearch`, `UserSearch`, or `RoomSearch` message.

## Captured adjacency

- Public Nicotine+ search-result performance and search-load reports exist, including issue #2128 and issue #3624, but these are performance/parser-adjacent rather than a direct duplicate of user-scoped response source admission.

## Rev0039 classification

```text
SEARCH-RESP-01A / U-163A: no direct public duplicate found in captured searches; public protocol basis and search-result adjacency exist.
SEARCH-RESP-01B: held because room source-set compatibility needs separate protocol/model work.
SEARCH-RESP-PARSE-BUDGET: public-adjacent through performance/search-load reports; not part of the user-source production packet.
```
