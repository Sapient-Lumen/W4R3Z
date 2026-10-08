# Field execution risk burndown rev0283

## Highest current risk

`FT-0181` is still externally gated: no real owner packet, no real returned CSV,
no accepted import, no live-window readout, and no closure signoff exist. The
most useful local work is still to prevent scratch artifacts from imitating field
progress.

Rev0283 burns down the pre-acceptance source-truth shortcut. The cube now keeps
candidate review, required source truth, accepted source truth, readiness, and
active change separate.

## Risks reduced

| Risk | Rev0283 reduction |
|---|---|
| A workbench review command makes a candidate packet look accepted | Router now emits `SRC2-CANDIDATE-NOT-ACCEPTED`, not bare `SRC2`, for proceed reviews. |
| A `ready_for_real_packet` ticket becomes a live/staged window | Router stops with `WAIT-FOR-REAL-SRC2-PACKET-BEFORE-LIVE-WINDOW` and no field command. |
| A live-window card is written from a readiness-only ticket | Recorder and shared guard require `ticket_state: active_change` for live/staged/paused/rolled-back/completed window states. |
| `SOURCE_TRUTH_REQUIRED=SRC2` is mistaken for accepted evidence | Audit and operator path now distinguish a requirement from an accepted source class. |
| Registry-only progress replaces field execution | The repair is in the router, recorder, shared guard, validators, smoke path, and operator surface. |

## What remains risky

The cube still lacks the thing that would let it move from candidate to field
change: a real accepted owner source packet. Until that exists, the correct
outcome after a ready ticket is a stop, not a live-window command.

## Next useful work

Use the router after any returned CSV/intake path. If it emits a candidate
review, preserve the candidate label. If it emits a ready-for-real-packet stop,
do not hand-write a live-window card. Only an accepted real source packet and an
`active_change` ticket should reach the live-window-card command.
