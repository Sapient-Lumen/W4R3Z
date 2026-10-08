# ROOM-SERVER-STATE coherence refactor — rev0026

## Canonical packet

**ROOM-SERVER-STATE-01 / U-111 + U-92** is now the canonical count-mismatch packet for server room/list aggregate arrays.

## Folded together

| id | Role | Reason |
|---|---|---|
| U-111 | JoinRoom lead | Parallel status/stats/slots/country arrays are indexed against the user array without validating equal counts. |
| U-92 | RoomList lead | Room arrays and user-count arrays are separately counted; mismatches can raise parser exceptions or preserve `None` counts. |

## Kept separate

| id | Decision | Reason |
|---|---|---|
| U-119 | separate | Private-room user-count offset/sort-column behavior needs its own UI arithmetic proof. |
| U-151 | separate | Additive stale RoomList inventory reconciliation is not malformed-count parsing. |
| U-240 | separate | Room-name semantic validation is a string policy issue, not an aggregate count issue. |
| U-245 | separate | SayChatroom sender-membership validation is a room-message policy issue. |
| U-252 | separate | RoomTicker absent-user validation is a ticker policy issue. |

## Fix composability note

The parser should reject malformed aggregate count mismatches before downstream room state or UI paths see partial data. A UI-only guard against `None` counts would hide symptoms while still allowing partial `UserData` objects and room-list state to propagate.
