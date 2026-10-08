# rev0040 public-overlap notes — SEARCH-RESP-01B-BUDDY

## Captured context

- Nicotine+'s public Soulseek protocol documentation describes `FileSearchResponse` as a peer message whose token comes from an original `FileSearch`, `UserSearch`, or `RoomSearch` server message.
- The same protocol page documents `UserSearch` as the server-message path used to search a specific user.
- Public GitHub issue adjacency exists for search results and buddy-list UX, including an open request to show whether a search-result username is already in the buddy list.

## Public duplicate status

No exact public duplicate of the rev0040 buddy-source snapshot packet was captured. The public context supports why `UserSearch`/`FileSearchResponse` token/source relationships and buddy-list result handling are relevant, but the cube keeps the duplicate classification conservative.

## Classification

```text
public-overlap: protocol and buddy/search-result adjacency
exact duplicate captured: no
production packet status: still valid inside cube, pending external human filing/review
```
