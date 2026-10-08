# Strict/front claim-capsule filing ledger — rev0050

File the minimum claim in each capsule, not the broadest family label. Keep public path-handling rows and broad release-note language as overlap context only.

|order|packet|capsule|nonclaims|
|---|---|---|---|
|1|U-123|handoff/rev0050/capsules/u-123.md|Not RCE, arbitrary file access, credential exposure, generic upload spoofing, or path traversal.|
|2|PB-01|handoff/rev0050/capsules/pb-01.md|Not a blanket PeerInit rejection, credential exposure, or generic username takeover claim.|
|3a|SEARCH-RESP-01A|handoff/rev0050/capsules/search-resp-01a.md|Not buddy/room policy, parser budget hardening, or all distributed-search behavior.|
|3b|SEARCH-RESP-01B-BUDDY|handoff/rev0050/capsules/search-resp-01b-buddy.md|Not live buddy-list-at-response-time enforcement; not room membership or parser budget.|
|3c|SEARCH-RESP-01C-ROOM|handoff/rev0050/capsules/search-resp-01c-room.md|Not empty-room crash behavior; not buddy/user mode; not parser budgets.|
|4a|SEARCH-RESP-PARSE-BUDGET-A|handoff/rev0050/capsules/search-resp-parse-budget-a.md|Not global uncompressed-message-size enforcement, result-count budget, or source admission.|
|4b|SEARCH-RESP-PARSE-BUDGET-B|handoff/rev0050/capsules/search-resp-parse-budget-b.md|Not source admission, UI display policy, or global network-message caps.|
