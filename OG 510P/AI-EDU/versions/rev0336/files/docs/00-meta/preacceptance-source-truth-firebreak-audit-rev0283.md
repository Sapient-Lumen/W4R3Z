# Pre-acceptance source-truth firebreak audit rev0283

## Risk named

The field lane had one more completion-looking shortcut after the reask gate. A
returned owner CSV could be intaken, seeded, reviewed, decided, and ticketed, but
before a real source packet was accepted the router still printed convenience
commands that used bare `SRC2` language. That created a laundering hazard: a
local candidate artifact could look like accepted owner evidence simply because a
later command needed a source class field.

The riskiest instance was the post-decision ticket path. A
`ready_for_real_packet` ticket says a bounded change is not yet authorized for a
live/staged window until the required real source packet is accepted. The old
router nevertheless emitted a live-window-card command with
`SOURCE_TRUTH_CLASS=SRC2`. That made "SRC2 required" too easy to read as "SRC2
already accepted."

## Repair

Rev0283 separates three states that must stay distinct:

1. `UNVERIFIED-OWNER-REPLY`: a returned local CSV before intake/review.
2. `SRC2-CANDIDATE-NOT-ACCEPTED`: a minimized owner-attested aggregate candidate
   that may proceed to the decision board, but is still not accepted evidence.
3. `SRC2` or stronger: a live-window source class only after the required real
   packet has been accepted and an `active_change` ticket exists.

The router now emits `SOURCE_TRUTH_CLASS=SRC2-CANDIDATE-NOT-ACCEPTED` for the
workbench-review proceed command. A `ready_for_real_packet` post-decision ticket
now routes to `WAIT-FOR-REAL-SRC2-PACKET-BEFORE-LIVE-WINDOW` with no field
command. The live-window-card recorder and shared guard reject staged, active,
paused, rolled-back, or completed window cards unless the source ticket is
`active_change`.

## Executable behavior

The clean scratch smoke path now proves the separation:

- after a valid workbench seed, `owner-field-next` recommends a workbench review
  with `SOURCE_TRUTH_CLASS=SRC2-CANDIDATE-NOT-ACCEPTED`;
- after a ready-for-real-packet ticket, `owner-field-next` emits no live-window
  command and names the missing real acceptance gate;
- after an active-change ticket, the router can emit a live-window-card command
  using `SRC2`, because the ticket state now carries the active-change boundary.

## Boundary

`SRC2-CANDIDATE-NOT-ACCEPTED` is not evidence, not custody, not closure, not
public-summary support, and not a public claim foundation. A
`ready_for_real_packet` ticket is only a readiness statement and source-class
requirement. It does not authorize live-window staging, active use, or source
truth upgrade.

## Validation coverage

- `tools/check_ft0181_field_next_action.py` verifies the candidate source class,
  the ready-ticket no-command stop, and the active-change live-window route.
- `tools/check_ft0181_live_window_card.py` verifies that a
  `ready_for_real_packet` ticket cannot source a live/staged window card.
- `tools/ft0181_field_guards.py` shares the ticket-state guard used by the
  router, recorder, and validators.
- `tools/record_ft0181_live_window_card.py` fails fast before writing a
  live-window artifact from a readiness-only ticket.
