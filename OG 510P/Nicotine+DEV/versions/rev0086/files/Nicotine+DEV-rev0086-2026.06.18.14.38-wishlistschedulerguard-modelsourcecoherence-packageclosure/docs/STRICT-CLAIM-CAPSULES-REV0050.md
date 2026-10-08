# Strict/front claim capsules — rev0050

Rev0050 adds one compact claim capsule per production-gated packet. Each capsule records the minimum claim, selected invariant/fix shape, evidence chain, non-claims, public-overlap boundary, and source-refresh caveat.

|order|packet|bundle|claim|
|---|---|---|---|
|1|U-123|01-transfer-session-identity|Same-user/same-token download TransferRequest handling must not replace a different live active owner, and stale cleanup must clear active_users[username][token] only when that slot still points to the cleanup Transfer object.|
|2|PB-01|02-peer-primary-election|An established same-user/same-type peer primary must not be replaced by a later claimed direct PeerInit or by generic secondary P/D/F post-init traffic while valid fallback and takeover-after-close remain compatible.|
|3a|SEARCH-RESP-01A|03-search-response-source-admission|For direct user searches, FileSearchResponse acceptance should require msg.username to be in the original requested user set for that token.|
|3b|SEARCH-RESP-01B-BUDDY|03-search-response-source-admission|For buddy-mode searches, accepted FileSearchResponse messages should be bound to the request-time buddy snapshot used to fan out UserSearch requests.|
|3c|SEARCH-RESP-01C-ROOM|03-search-response-source-admission|For room-mode searches with a usable non-empty joined-room member snapshot, accepted FileSearchResponse messages can be bound to that request-time snapshot while preserving broad compatibility when no snapshot exists.|
|4a|SEARCH-RESP-PARSE-BUDGET-A|04-search-response-parser-budget|The FileSearchResponse parser should reject overlong compressed username prefixes before inflating username_len + 4 bytes solely to reach an invalid or unknown token.|
|4b|SEARCH-RESP-PARSE-BUDGET-B|04-search-response-parser-budget|After token validation, FileSearchResponse parsing should bound accepted public/private result-list counts before materializing accepted result bodies.|

No new private packet is promoted in rev0050.
