# Mission kernel rev0276

The mission is still to make AI in education accountable to learning, agency, access, teacher capacity, and institutional truth rather than to tool adoption. Rev0276 narrows the live execution path again: a first real owner packet must pass from contact clock to returned CSV, intake, seed, review, and now a five-slice first-packet decision artifact before any change ticket can exist.

## Current live kernel

1. Prepare the bounded `AIEDU-SR-003` owner packet.
2. Record a local send log only after the human send/adaptation.
3. Record the bounded contact clock from that send log.
4. Intake a real returned CSV only through the active source contact clock.
5. Create a `NOT_ACCEPTED` workbench seed only from a valid intake bundle.
6. Record a minimized workbench review only from a valid seed.
7. Record a minimized five-slice first-packet decision only from a proceed-capable workbench review.
8. Do not open custody, public-summary, live-window, or closure paths until a post-decision change ticket exists.

## What changed in rev0276

The first-packet decision board is no longer only a prose surface. `make owner-field-next` now emits a bounded `make owner-first-packet-decision ...` command when the latest scratch artifact is a valid `PROCEED-DECISION-BOARD` workbench review. The decision artifact remains `NOT_ACCEPTED` and `not_evidence`.

## What still counts as progress

Progress is not a new registry row. Progress is one of these:

- a real external send/adaptation followed by a local send log;
- a bounded contact clock;
- a real returned owner CSV tied to that clock;
- a source-clock-gated intake bundle;
- a seed, review, and first-packet decision that preserve non-evidence boundaries; or
- a bounded no-owner-packet record when the source re-ask clock expires.

## What must not change

No local field artifact can close `FT-0181`, prove a learning or service outcome, upgrade public claims, or become custody evidence. The new decision-board record may source a post-decision change ticket only.
