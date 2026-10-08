# rev0026 public-overlap notes — ROOM-SERVER-STATE-01 / U-111 + U-92

Classification: **candidate no direct public match found / public-adjacent parser and room-list UI hardening**.

## Exact/direct searches captured

| Search | Result |
|---|---|
| `"RoomList" "TypeError"` | No direct Nicotine+ issue result observed in captured search. |
| `"RoomList" "NoneType"` | No direct Nicotine+ issue result observed in captured search. |
| `"room-list" "humanize"` | No direct Nicotine+ issue result observed in captured search. |
| `"JoinRoom" "IndexError"` | No direct Nicotine+ issue result observed in captured search. |

## Public-adjacent material

- Public Room List / Public Room Feed crash reports exist, but the captured report is not the specific count-array mismatch or `humanize(None)` path.
- Public GTK/list crash reports exist around other user-list or interest-list surfaces, but they are not a direct `JoinRoom` aggregate count mismatch report.
- Broad malformed-message/parser-size hardening is upstream-adjacent because 3.3.11 RC material includes network-message-size hardening.

## Cube decision

This is verified and worth keeping as a regression-hardening packet, but not a clean novelty claim and not strict-promoted.
