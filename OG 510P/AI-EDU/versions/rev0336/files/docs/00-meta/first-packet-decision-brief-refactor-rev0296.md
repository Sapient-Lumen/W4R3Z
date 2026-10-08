# rev0296 first-packet decision brief refactor

## What changed

`rev0296` compresses the next risky local seam in `FT-0181`: after a human has
recorded a `PROCEED-DECISION-BOARD` workbench review, the five-slice first-packet
decision command is still dense enough to stall or be filled incorrectly. The
archive should not automate the board decision, but it can prepare a minimized
scratch-local board brief and exact bounded command skeletons.

New helper:

```bash
make owner-first-packet-decision-brief REVIEW=scratch/.../workbench-review.json
```

`make owner-field-work` may now safely prepare this decision brief when the router
selects `PREPARE-FIRST-PACKET-DECISION-BRIEF`. It still stops before any human
board choice or decision record.

## What the brief does

The brief validates the scratch-local `PROCEED-DECISION-BOARD` review, writes a
one-screen board handoff, and emits bounded `owner-first-packet-decision` command
skeletons for five route families:

- `conservative_watch`
- `sandbox_adjustment`
- `suppress_or_quarantine`
- `pilot_with_expiry_candidate`
- `no_public_change_watch`

The brief copies no owner answers, raw CSV rows, workbench-review text, contact
details, learner identifiers, protected facts, screenshots, public claim text, or
security payloads.

## Boundary

The decision brief is not a decision-board record. It cannot source custody,
acceptance, activation, service-record mutation, public-summary support,
lifecycle movement, a change ticket, live-window activity, or closure.

The only valid next human-owned step after the brief is to choose one bounded
route and run `make owner-first-packet-decision ...` with the confirmation token
`human-recorded-five-slice-decision-board`.

## Waste corrected

This revision also corrects a stale label in the post-decision change-ticket
summary: that surface is a change-ticket record, not a live-window card. The bug
was small but dangerous because stale labels make later operators more likely to
mistake readiness for activation.
