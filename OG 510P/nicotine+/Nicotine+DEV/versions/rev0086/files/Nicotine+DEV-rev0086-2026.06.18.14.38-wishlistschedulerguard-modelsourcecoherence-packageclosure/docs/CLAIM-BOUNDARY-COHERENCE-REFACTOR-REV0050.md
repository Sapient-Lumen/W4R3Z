# Claim-boundary coherence refactor — rev0050

This audit/refactor pass prevents filing drift by separating packet-specific claims from adjacent public or broad release-note language.

|scope|keep|separate|action|
|---|---|---|---|
|U-123|transfer-session identity|path traversal, generic upload spoofing, PB-01|claim capsule narrows to active-owner collision|
|PB-01|peer primary election|username release-note wording, U-123, path handling|claim capsule emphasizes established-primary compatibility|
|SEARCH-RESP source series|user/buddy/room source admission|parser budgets, empty-room crash, broad distributed-search wording|three source capsules with mode-specific carve-outs|
|SEARCH-RESP parser-budget series|prefix and result-list budgets|source admission, UI policy, global message caps|two parser capsules with distinct materialization points|
|PUBLIC-PATH-JOIN rows|public-watch-only|all seven private packets|non-claim ledger prevents private-packet drift|
