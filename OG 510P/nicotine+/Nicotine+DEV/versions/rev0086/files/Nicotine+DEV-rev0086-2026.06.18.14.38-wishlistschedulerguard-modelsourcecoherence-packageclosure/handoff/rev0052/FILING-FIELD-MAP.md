# rev0052 filing-field map

This handoff layer maps every production-gated packet to the exact filing fields a reviewer needs before external action: minimum claim, selected invariant, report, fix/patch material, regression evidence, source anchors, non-claims, and the current-source refresh caveat.

|order|packet|bundle|field capsule|review focus|
|---|---|---|---|---|
|1|U-123|01-transfer-session-identity|handoff/rev0052/fields/u-123.md|transfer-session active-owner collision and identity-aware deactivation|
|2|PB-01|02-peer-primary-election|handoff/rev0052/fields/pb-01.md|peer primary election with fallback compatibility|
|3a|SEARCH-RESP-01A|03-search-response-source-admission|handoff/rev0052/fields/search-resp-01a.md|direct user-search source binding|
|3b|SEARCH-RESP-01B-BUDDY|03-search-response-source-admission|handoff/rev0052/fields/search-resp-01b-buddy.md|buddy-mode request-time source snapshot|
|3c|SEARCH-RESP-01C-ROOM|03-search-response-source-admission|handoff/rev0052/fields/search-resp-01c-room.md|room-mode membership-snapshot source binding when available|
|4a|SEARCH-RESP-PARSE-BUDGET-A|04-search-response-parser-budget|handoff/rev0052/fields/search-resp-parse-budget-a.md|compressed username-prefix cap before token read|
|4b|SEARCH-RESP-PARSE-BUDGET-B|04-search-response-parser-budget|handoff/rev0052/fields/search-resp-parse-budget-b.md|accepted public/private result-list count budget|

Guardrail: rev0052 does not promote new private packets. It adds a filing-field crosswalk and a lightweight public web spotcheck only; a full current upstream checkout remains the top pre-filing gate.
