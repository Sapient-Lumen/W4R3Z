# Draft skeleton — PB-01 peer connection primary-election binding

Status: **strict/front-lane report-candidate, not production-ready disclosure text**.

## Candidate lead

Treat U-168 and U-176 as one coherent PB-01 report-candidate:

- U-168 captures direct `PeerInit` replacement for P/D connections.
- U-176 captures secondary post-init promotion for P/D/F connections.
- U-165 is PierceFireWall support context, not a separate first report here.

## Current evidence

The rev0010 state-machine probe confirms both U-168 and U-176 across 3.3.10, 3.3.x, and master. It is handler/state-machine evidence, not a polished two-client live-flow exploit.

## Needed before use

- Maintainer-grade current-behavior reproducer derived from `tools/probe_rev0010_pb01_connection_state_machine.py`.
- Compatibility review for legitimate direct/indirect reconnect and fallback behavior.
- Final public/private overlap check for exact invariant wording.
- Fixed-behavior regression once a patch shape exists.
