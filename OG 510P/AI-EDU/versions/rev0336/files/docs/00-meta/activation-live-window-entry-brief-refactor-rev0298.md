# rev0298 activation/live-window entry brief refactor

## What changed

`rev0298` compresses the next risky seam in `FT-0181`: after a human records a
post-decision change ticket, the archive had two brittle late-field exits.

- `ready_for_real_packet` pointed toward activation receipt recording, but the
  operator still had to carry a dense same-source-packet command without a small
  local handoff.
- `active_change` pointed straight at the live-window card command, which made it
  too easy to confuse an active ticket with an already-started bounded window.

New helper:

```bash
make owner-activation-live-window-brief \
  TICKET=scratch/.../post-decision-change-ticket.json
```

`make owner-field-work` may now safely prepare this brief when the router selects
`PREPARE-ACTIVATION-LIVE-WINDOW-BRIEF`. It reruns the router and stops at the
human-owned activation-receipt or live-window-card boundary.

## What the brief does

The brief validates only a scratch-local `ready_for_real_packet` or
`active_change` post-decision ticket and writes a one-screen entry handoff.

For `ready_for_real_packet`, it emits only the same-source activation-receipt
command template and the follow-on active-change ticket skeleton. It emits no
live-window card command.

For `active_change`, it emits bounded live-window card command templates for a
small staged/active/paused/quarantined path. It does not request another
activation receipt.

## Boundary

The brief is not an activation receipt. It is not an active-change ticket. It is
not a live-window card. It is not evidence, SRC2+ acceptance, custody evidence,
public-summary support, lifecycle movement, service-record mutation, or closure.

The refactor reduces operator drop-off at the point where real packet readiness
must not be laundered into live-window authority.
