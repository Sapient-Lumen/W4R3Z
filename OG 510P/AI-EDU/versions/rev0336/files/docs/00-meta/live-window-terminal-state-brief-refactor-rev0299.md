# rev0299 live-window terminal-state brief refactor

## What changed

`rev0299` compresses the next risky seam in `FT-0181`: after a staged or active
live-window card exists, the archive previously told the operator to operate
within the card and come back once a terminal state existed. That was safe, but
it was also a drop-off point: the terminal card command was dense, and the path
from nonterminal card to readout could stall or blur into closure language.

New helper:

```bash
make owner-live-window-terminal-brief \
  CARD=scratch/.../live-window-card.json
```

`make owner-field-work` may now safely prepare this brief when the router selects
`PREPARE-LIVE-WINDOW-TERMINAL-STATE-BRIEF`. It reruns the router and stops at
the human-owned terminal-card boundary.

## What the brief does

The brief validates only a scratch-local `staged` or `active` live-window card
and writes a one-screen handoff with bounded command skeletons for exactly one
terminal card state:

- `paused`
- `rolled_back`
- `completed_no_closure`
- `quarantined`

It preserves the source card hash, source ticket reference, source-truth class,
window counts, stop/rollback controls, and no-expansion confirmations. It writes
no terminal card and records no readout.

## Boundary

The brief is not a live-window card. It is not a readout. It is not evidence,
SRC2+ acceptance, custody evidence, public-summary support, lifecycle movement,
service-record mutation, or closure.

The refactor reduces operator drop-off at the point where a real bounded window
must become a terminal local card before any end-of-window readout can happen.
