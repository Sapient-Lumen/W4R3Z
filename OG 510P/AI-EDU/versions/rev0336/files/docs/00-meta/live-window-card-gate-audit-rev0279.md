# Live-window card gate audit rev0279

## Question

After the mission/waste read, can a valid post-decision change ticket or
live-window card still be mistaken for permission to run beyond bounds, mutate
service records, promote lifecycle state, change public language, or approach
closure?

## Finding

The rev0278 card gate remains structurally sound. The newly found weakness was
not the card itself; it was re-entry freshness. The live followthrough queue
still pointed at the older rev0276 first-packet decision gate, so an operator
could enter the archive through stale instructions even though the card gate was
present and lint-valid.

## Change

Rev0279 keeps the rev0278 card mechanics and adds a freshness boundary around
the live queue. A queued followthrough item must now:

- point to an existing current-revision surface;
- name the current revision in `why_live`, `current_blocker`, and `current_action`;
- remain synchronized with the receipt live/closed followthrough lists.

The card itself still must source a scratch-local `post-decision-change-ticket.json`,
revalidate it, preserve its hash and core route fields, keep `NOT_ACCEPTED` and
`not_evidence`, and store only window states, count classes, controls, and routes.

## Blocks preserved

The gate still blocks non-scratch outputs, tampered or accepted source tickets,
active/staged cards without `SRC2+` source truth, overlong windows, missing stop
or rollback controls, raw learner data, protected facts, security payloads,
contact details, copied owner answers, public-claim upgrades, custody moves, and
closure support.

## Boundary

No live-window card, summary, route, confirmation, audit surface, or freshness
check is real pilot evidence, custody evidence, source acceptance, public-summary
support, or closure support. `FT-0181` remains live until the full real-import
closeout chain is met.
