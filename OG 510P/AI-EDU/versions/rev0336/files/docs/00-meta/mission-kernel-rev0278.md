# Mission kernel rev0278

The mission remains to make AI in education accountable to learning, agency,
access, teacher capacity, and institutional truth rather than to tool adoption.
Rev0278 narrows the live execution path again: a first real owner packet must
now pass from contact clock to returned CSV, intake, seed, review, first-packet
decision, post-decision change ticket, and live-window stop/rollback card before
any readout, service-record edit, lifecycle move, custody, public-summary change,
or closure step.

## Current live kernel

1. Prepare the bounded `AIEDU-SR-003` owner packet.
2. Record a local send log only after the human send/adaptation.
3. Record the bounded contact clock from that send log.
4. Intake a real returned CSV only through the active source contact clock.
5. Create a `NOT_ACCEPTED` workbench seed only from a valid intake bundle.
6. Record a minimized workbench review only from a valid seed.
7. Record a minimized five-slice first-packet decision only from a proceed-capable workbench review.
8. Record a minimized post-decision change ticket only from a valid first-packet decision.
9. Record a bounded live-window stop/rollback card only from a valid change ticket.
10. Do not open a readout, service record, lifecycle, custody, public-summary,
    or closure path until the live-window card reaches a terminal/readout-ready
    state and the end-of-window gate is used.

## What changed in rev0278

The live-window stop/rollback card is no longer only a prose surface.
`make owner-field-next` now emits a bounded `make owner-live-window-card ...`
command when the latest scratch artifact is a valid `post-decision-change-ticket.json`.
The card artifact remains `NOT_ACCEPTED` and `not_evidence`.

## What still counts as progress

Progress is not a new registry row. Progress is one of these:

- a real external send/adaptation followed by a local send log;
- a bounded contact clock;
- a real returned owner CSV tied to that clock;
- a source-clock-gated intake bundle;
- a seed, review, first-packet decision, post-decision ticket, and live-window
  card that preserve non-evidence boundaries; or
- a bounded no-owner-packet record when the source re-ask clock expires.

## What must not change

No local field artifact can close `FT-0181`, prove a learning or service outcome,
upgrade public claims, become custody evidence, or modify service records. The
new live-window card may source the end-of-window readout gate only after a
terminal/readout-ready state; it cannot itself authorize closure or public claims.
