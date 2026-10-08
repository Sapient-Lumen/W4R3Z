# rev0028 web/public-overlap notes — SEARCH-SEND-POLICY-01

Scope: U-174 and U-247.

## Sources searched / checked

- Official protocol documentation: `FileSearch`, `UserSearch`, `RoomSearch`, `FileSearchRequest`, `FileSearchResponse`, and distributed search behavior.
- Nicotine+ GitHub issue search for exact plugin hooks:
  - `"search_request_notification"`
  - `"distrib_search_notification"`
- Nicotine+ GitHub issue search for search/geoblock terms:
  - `"FileSearch" "geoblock"`
  - `"geoblock" "search"`
  - `"responding to searches"`
- Public issues/release notes used as adjacency:
  - #891 GeoBlock Not Blocking — broad geoblock symptom history.
  - #3624 Heavy UI input lagging affected by responding to searches option — search responder load adjacency.
  - #3471 Plugin System notification for search results — plugin/search notification adjacency, not this exact request-policy ordering.
  - #1786 Plugin Debugger missing notifications — exact hook names appear in public history, so plugin hook existence is not novel.
  - 3.3.11 RC release notes — broad search/distributed/network-message hardening context.

## Conclusion

No direct public match was found in this pass for the exact combined invariant:

```text
inbound server/distributed search request -> core response policy may reject/accept using username-only permission context -> plugin notification still emits even when core rejects -> response permission/geoblock lacks requester/source IP binding or send-time revalidation
```

However, the packet is public-adjacent rather than clean novelty because public geoblock symptoms, search-responder load symptoms, and plugin/search notification enhancement history already exist.

## Classification

```text
U-174: candidate no direct exact public match found / public-adjacent; not strict-promoted.
U-247: public-adjacent plugin/search notification behavior; support under SEARCH-SEND-POLICY-01, not standalone strict item.
```
