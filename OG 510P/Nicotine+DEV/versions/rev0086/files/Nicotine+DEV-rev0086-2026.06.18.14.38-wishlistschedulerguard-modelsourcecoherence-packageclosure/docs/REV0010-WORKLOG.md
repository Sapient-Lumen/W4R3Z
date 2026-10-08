# rev0010 worklog

## Focus

This revision stayed on the riskiest unfinished peer-binding work rather than broad registry expansion. The concrete target was PB-01: peer-connection primary election and replacement behavior.

## Completed

- Built `tools/probe_rev0010_pb01_connection_state_machine.py`.
- Ran it against all three archived source lanes from the external rev0003 bundle.
- Confirmed U-168 direct PeerInit replacement for peer (`P`) and distributed (`D`) connections.
- Confirmed U-176 secondary-to-primary promotion for peer (`P`), distributed (`D`), and file-transfer (`F`) connections.
- Confirmed a valid PierceFireWall support path where a secondary peer connection later becomes primary after ordinary post-init peer traffic.
- Added compact source traces for the affected handler paths.
- Refactored PB-01 coherence so U-168 and U-176 are one report-candidate, U-165 is support, and U-171/U-181 remain separate backlog.
- Merged U-40 into U-145 to reduce duplicate address-validation rows.

## Not completed

- No two-client/live-socket integration harness yet.
- No maintainer-ready PB-01 unit test yet.
- No final private/maintainer overlap determination.
- No production-ready disclosure text.

## Next best revision

Convert PB-01 into a maintainer-grade current-behavior test/report skeleton, while explicitly testing legitimate reconnect/fallback compatibility. Do not widen the queue until PB-01 has the same packet quality U-123 reached in rev0009.
