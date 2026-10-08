# Live-window card gate audit rev0278

## Question

Can a valid post-decision change ticket still be mistaken for permission to run a
live window, mutate service records, promote lifecycle state, change public
language, or approach closure?

## Finding

Before rev0278, the router sent the operator to the prose
`ft0181-live-window-stop-rollback-card.md` surface. That was better than nothing,
but it left the next execution step unrecorded and easy to over-narrate. A card
could be described in prose without preserving the source ticket, source-truth
class, count bounds, no-expansion rule, human pause ability, fallback route, or
readout-only next step.

## Change

Rev0278 adds:

- `tools/record_ft0181_live_window_card.py`
- `tools/check_ft0181_live_window_card.py`
- `owner-live-window-card` in `Makefile`
- `owner_live_window_card_integrity_error(...)` in `tools/ft0181_field_guards.py`
- router recognition of `scratch/owner-live-window-cards/**/live-window-card.json`

A valid card must source a scratch-local `post-decision-change-ticket.json`,
revalidate it, preserve its hash and core route fields, keep `NOT_ACCEPTED` and
`not_evidence`, and store only window states, count classes, controls, and routes.

## Blocks

The gate blocks:

- non-scratch or release-controlled outputs;
- tampered or accepted source tickets;
- active/staged cards without `SRC2+` source truth;
- blocked cards that pretend to have live days or allowed live activities;
- windows longer than fourteen days;
- missing stop triggers, rollback steps, rollback owner roles, or prohibitions;
- live/staged cards without no-expansion, human-pause, and fallback-route confirmation;
- raw learner data, protected facts, security payloads, contact details, copied owner answers, and public-claim upgrades.

## Refactor effect

The first-read path now names the executable sequence rather than another prose
surface. A post-decision ticket routes to a card recorder; a terminal/readout-ready
card routes to the end-of-window readout gate. The card itself remains local and
cannot authorize closure.

## Boundary

No live-window card, summary, route, confirmation, or audit surface is real pilot
evidence, custody evidence, source acceptance, public-summary support, or closure
support. `FT-0181` remains live until the full real-import closeout chain is met.
